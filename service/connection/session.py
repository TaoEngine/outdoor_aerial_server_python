from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any, Callable, Coroutine

from aioquic.h3.connection import H3Connection
from aioquic.h3.events import (
    DataReceived,
    DatagramReceived,
    WebTransportStreamDataReceived,
)
from aioquic.quic.connection import (
    QuicConnection,
    stream_is_client_initiated,
    stream_is_unidirectional,
)
from yarl import URL

from service.connection.handler import WebTransportHandler, WebTransportSessionContext
from service.connection.stream import WebTransportStream, WebTransportStreamConfig
from service.connection.types import TransportPeerName

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WebTransportClientInfo:
    """标准化后的客户端地址信息。"""

    host: str
    """客户端主机名或 IP。"""

    port: int | None
    """客户端端口，无法解析时为 `None`。"""

    def __str__(self) -> str:
        return f"{self.host}:{self.port}" if self.port is not None else self.host

    @classmethod
    def from_peername(
        cls, peername: TransportPeerName | None
    ) -> "WebTransportClientInfo | None":
        """将传输层 `peername` 转换为结构化客户端地址。"""
        if peername is None:
            return None

        host, port = peername[0], peername[1]
        return cls(host=host, port=port)


@dataclass(frozen=True)
class WebTransportSessionInfo:
    """业务处理器可读取的会话元信息。"""

    session_id: int
    """会话对应的 HTTP/3 stream ID。"""

    path: URL
    """会话请求 URL。"""

    client: WebTransportClientInfo | None
    """标准化后的客户端地址。"""


class WebTransportSession(WebTransportSessionContext):
    """
    与单个处理器实例绑定的 WebTransport 会话。

    生命周期由 `run` 驱动：
    1. 接受握手；
    2. 触发处理器 `on_session_ready`；
    3. 分发子流 / datagram / 连接事件；
    4. 统一执行关闭与资源回收。
    """

    def __init__(
        self,
        h3: H3Connection,
        quic: QuicConnection,
        session_info: WebTransportSessionInfo,
        handler: WebTransportHandler,
        transmit: Callable[[], None],
    ) -> None:
        """保存依赖并初始化会话运行时状态。"""
        self._h3 = h3
        self._quic = quic
        self._session_info = session_info
        self._handler = handler
        self._handler.bind_context(self)
        self._transmit = transmit

        self._accepted = False
        self._closed = False
        self._close_code = 0
        self._close_reason = ""
        self._closed_event = asyncio.Event()

        self._streams: dict[int, WebTransportStream] = {}
        self._tasks: set[asyncio.Task[None]] = set()

    @property
    def session_id(self) -> int:
        """当前会话的 HTTP/3 stream ID。"""
        return self._session_info.session_id

    def _log_prefix(self) -> str:
        """统一会话日志上下文，便于跨场景检索。"""
        return (
            f"session_id={self.session_id} "
            f"path={self._session_info.path.path_qs} "
            f"client={self._session_info.client} "
            f"handler={type(self._handler).__name__}"
        )

    async def run(self) -> None:
        """启动会话主流程并在退出时保证资源回收。"""
        self._accept()
        try:
            await self._handler.on_session_ready()
            await self._closed_event.wait()
        except Exception:
            log.exception(
                f"处理器会话启动回调异常，强制关闭会话（场景: on_session_ready）: {self._log_prefix()}"
            )
            self._mark_closed(
                code=1,
                reason="处理器 on_session_ready 回调异常",
                send=True,
                scene="on_session_ready 回调异常",
            )
        finally:
            await self._finalize()

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        """由服务端主动创建 WebTransport 子流。"""
        if self._closed:
            raise RuntimeError("会话已关闭，无法创建新子流")
        is_unidirectional = not bidirectional
        stream_id = self._h3.create_webtransport_stream(
            session_id=self.session_id,
            is_unidirectional=is_unidirectional,
        )
        stream = WebTransportStream(
            config=WebTransportStreamConfig(
                stream_id=stream_id,
                bidirectional=bidirectional,
                readable=bidirectional,
                writable=True,
            ),
            send_stream_data=self._quic.send_stream_data,
            transmit=self._transmit,
        )
        self._streams[stream_id] = stream
        stream_type = "双向" if bidirectional else "单向"
        log.info(
            f"服务端创建子流成功（场景: 主动创建{stream_type}流）: stream_id={stream_id} {self._log_prefix()}"
        )
        return stream

    def send_datagram(self, data: bytes) -> None:
        """由服务端主动发送 datagram。"""
        if self._closed:
            log.debug(
                f"会话已关闭，忽略 datagram 发送请求（场景: 关闭后发送）: bytes={len(data)} {self._log_prefix()}"
            )
            return
        self._h3.send_datagram(stream_id=self.session_id, data=data)
        self._transmit()
        log.debug(
            f"服务端 datagram 已发送（场景: 主动发送）: bytes={len(data)} {self._log_prefix()}"
        )

    def close_session(self, error: bool = False, reason: str | None = None) -> None:
        """由处理器主动结束会话。"""
        self._mark_closed(
            code=1 if error else 0,
            reason=reason,
            send=True,
            scene="处理器主动关闭会话",
        )

    def handle_stream_event(self, event: WebTransportStreamDataReceived) -> None:
        """处理子流数据事件，并在首次出现时创建本地流对象。"""
        stream_id = event.stream_id
        stream = self._streams.get(stream_id)
        is_uni = stream_is_unidirectional(stream_id)
        is_client = stream_is_client_initiated(stream_id)

        if stream is None:
            bidirectional = not is_uni
            stream = WebTransportStream(
                config=WebTransportStreamConfig(
                    stream_id=stream_id,
                    bidirectional=bidirectional,
                    readable=(not is_uni) or is_client,
                    writable=(not is_uni) or (not is_client),
                ),
                send_stream_data=self._quic.send_stream_data,
                transmit=self._transmit,
            )
            self._streams[stream_id] = stream
            if is_client:
                if is_uni:
                    log.info(
                        f"收到客户端新建单向流（场景: 客户端上行流）: stream_id={stream_id} {self._log_prefix()}"
                    )
                    self._spawn_task(
                        self._handler.on_stream_unidirectional(stream),
                        scene=f"客户端单向流回调 stream_id={stream_id}",
                    )
                else:
                    log.info(
                        f"收到客户端新建双向流（场景: 客户端双向流）: stream_id={stream_id} {self._log_prefix()}"
                    )
                    self._spawn_task(
                        self._handler.on_stream_bidirectional(stream),
                        scene=f"客户端双向流回调 stream_id={stream_id}",
                    )

        if stream.readable:
            stream._feed(event.data, event.stream_ended)
            if event.stream_ended:
                log.debug(
                    f"子流接收完成（场景: 对端结束发送）: stream_id={stream_id} bytes={len(event.data)} {self._log_prefix()}"
                )
        elif event.data or event.stream_ended:
            log.warning(
                f"收到不可读子流数据，已忽略（场景: 流方向不匹配）: "
                f"stream_id={stream_id} bytes={len(event.data)} ended={event.stream_ended} {self._log_prefix()}"
            )

    def handle_datagram(self, event: DatagramReceived) -> None:
        """处理客户端 datagram。"""
        if self._closed:
            log.debug(
                f"会话已关闭，忽略客户端 datagram（场景: 关闭后仍有数据）: bytes={len(event.data)} {self._log_prefix()}"
            )
            return
        self._spawn_task(
            self._handler.on_datagram(event.data),
            scene=f"datagram 回调 bytes={len(event.data)}",
        )

    def handle_session_data(self, event: DataReceived) -> None:
        """处理会话控制流事件（主要关注结束信号）。"""
        if event.stream_ended:
            self._mark_closed(
                code=0,
                reason="客户端关闭会话控制流",
                send=False,
                scene="客户端结束会话控制流",
            )
        elif event.data:
            log.warning(
                f"收到会话控制流数据，按协议忽略（场景: 非预期控制流载荷）: bytes={len(event.data)} {self._log_prefix()}"
            )

    def handle_connection_terminated(self, code: int, reason: str) -> None:
        """底层 QUIC 连接终止时关闭会话。"""
        self._mark_closed(
            code=code,
            reason=reason,
            send=False,
            scene="底层 QUIC 连接终止",
        )

    def _accept(self) -> None:
        """向客户端返回 WebTransport 会话建立成功状态。"""
        if self._accepted:
            return
        self._accepted = True
        self._h3.send_headers(
            stream_id=self.session_id,
            headers=[(b":status", b"200")],
            end_stream=False,
        )
        self._transmit()
        log.info(f"WebTransport 会话握手成功（场景: 返回 200）: {self._log_prefix()}")

    def _mark_closed(
        self, code: int, reason: str | None, send: bool, scene: str
    ) -> None:
        """统一记录关闭状态，按需向客户端发送结束信号。"""
        if self._closed:
            log.debug(f"会话重复关闭请求已忽略（场景: {scene}）: {self._log_prefix()}")
            return
        self._closed = True
        self._close_code = code
        self._close_reason = reason or ""
        close_reason = self._close_reason or "-"
        log.info(
            f"会话进入关闭流程（场景: {scene}）: code={code} reason={close_reason} send_fin={send} {self._log_prefix()}"
        )
        if send:
            self._h3.send_data(
                stream_id=self.session_id,
                data=b"",
                end_stream=True,
            )
            self._transmit()
        self._closed_event.set()

    async def _finalize(self) -> None:
        """执行收尾逻辑：关闭流、取消任务、回调处理器。"""
        close_reason = self._close_reason or "-"
        log.info(
            f"会话资源回收开始（场景: finalize）: streams={len(self._streams)} tasks={len(self._tasks)} "
            f"code={self._close_code} reason={close_reason} {self._log_prefix()}"
        )
        for stream in self._streams.values():
            stream.close()
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        try:
            await self._handler.on_session_closed(
                error=self._close_code != 0,
                reason=self._close_reason or None,
            )
        except Exception:
            log.exception(
                f"处理器会话关闭回调异常（场景: on_session_closed）: {self._log_prefix()}"
            )

    def _spawn_task(self, coro: Coroutine[Any, Any, None], scene: str) -> None:
        """注册并追踪会话内异步任务。"""
        task = asyncio.create_task(coro, name=f"session={self.session_id} {scene}")
        self._tasks.add(task)
        task.add_done_callback(self._handle_task_done)

    def _handle_task_done(self, task: asyncio.Task[None]) -> None:
        """处理会话异步任务的结束结果，避免异常静默丢失。"""
        self._tasks.discard(task)
        task_scene = task.get_name()
        try:
            task.result()
        except asyncio.CancelledError:
            log.debug(
                f"会话子任务已取消（场景: 关闭清理）: task={task_scene} {self._log_prefix()}"
            )
        except Exception:
            log.exception(
                f"处理器子任务异常（场景: {task_scene}）: {self._log_prefix()}"
            )
