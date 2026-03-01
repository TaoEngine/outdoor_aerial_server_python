import asyncio
from dataclasses import dataclass
import logging

from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import (
    DataReceived,
    DatagramReceived,
    H3Event,
    HeadersReceived,
    WebTransportStreamDataReceived,
)
from aioquic.quic.events import ConnectionTerminated, ProtocolNegotiated, QuicEvent
from yarl import URL

from service.connection.router import WebTransportRouter
from service.connection.session import (
    WebTransportClientInfo,
    WebTransportSession,
    WebTransportSessionInfo,
)
from service.connection.types import TransportPeerName

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class HeaderInfo:
    """从 HTTP/3 请求头中提取出的关键字段。"""

    target: URL
    """请求目标 URL（包含路径与查询参数）。"""

    method: str | None
    """HTTP 方法（例如 `CONNECT`）。"""

    protocol: str | None
    """`:protocol` 字段（例如 `webtransport`）。"""

    @property
    def is_webtransport(self) -> bool:
        """是否为 WebTransport 会话握手请求。"""
        return self.method == "CONNECT" and self.protocol == "webtransport"

    @classmethod
    def from_headers(cls, headers: list[tuple[bytes, bytes]]) -> "HeaderInfo":
        """将 `aioquic` header 列表转换为结构化信息。"""
        header_dict = {key.decode(): value.decode() for key, value in headers}
        try:
            scheme = header_dict[":scheme"]
            authority = header_dict[":authority"]
            path = header_dict[":path"]
        except KeyError as exc:
            raise ValueError(f"缺少必需请求头: {exc.args[0]}") from exc

        target = URL.build(
            scheme=scheme,
            authority=authority,
            path=path,
        )
        return cls(
            target=target,
            method=header_dict.get(":method"),
            protocol=header_dict.get(":protocol"),
        )


class WebTransportProtocol(QuicConnectionProtocol):
    def __init__(self, *args, app: WebTransportRouter, **kwargs):
        super().__init__(*args, **kwargs)
        self._h3: H3Connection | None = None
        self._app: WebTransportRouter | None = app
        self._sessions: dict[int, WebTransportSession] = {}
        """一个 `session_id` 对应一个会话实例。"""

    def quic_event_received(self, event: QuicEvent) -> None:
        match event:
            case ProtocolNegotiated():
                self._h3 = H3Connection(self._quic, enable_webtransport=True)
            case ConnectionTerminated():
                for session in self._sessions.values():
                    session.handle_connection_terminated(
                        code=event.error_code, reason=event.reason_phrase
                    )

        if self._h3 is not None:
            for h3_event in self._h3.handle_event(event):
                self._handle_h3_event(h3_event)
            self.transmit()

    def _handle_h3_event(self, event: H3Event) -> None:
        match event:
            case HeadersReceived():
                self._handle_headers(event)
            case WebTransportStreamDataReceived():
                # 子流事件：通过 event.session_id 找到所属会话
                session = self._sessions.get(event.session_id)
                if session is not None:
                    session.handle_stream_event(event)
            case DatagramReceived():
                # 数据报事件：stream_id 即 session_id
                session = self._sessions.get(event.stream_id)
                if session is not None:
                    session.handle_datagram(event)
            case DataReceived():
                session = self._sessions.get(event.stream_id)
                if session is not None:
                    session.handle_session_data(event)

    def _handle_headers(self, event: HeadersReceived) -> None:
        try:
            header = HeaderInfo.from_headers(event.headers)
        except ValueError as exc:
            log.warning(
                "WebTransport 握手请求头不完整: stream_id=%s detail=%s",
                event.stream_id,
                exc,
            )
            if self._h3 is not None:
                self._h3.send_headers(
                    stream_id=event.stream_id,
                    headers=[(b":status", b"400")],
                    end_stream=True,
                )
                self.transmit()
            return

        if not header.is_webtransport:
            return
        if self._h3 is None or self._app is None:
            return

        raw_peername = (
            self._transport.get_extra_info("peername") if self._transport else None
        )
        peername: TransportPeerName | None = None
        if (
            isinstance(raw_peername, tuple)
            and len(raw_peername) >= 2
            and isinstance(raw_peername[0], str)
            and isinstance(raw_peername[1], int)
        ):
            host, port = raw_peername[0], raw_peername[1]
            if (
                len(raw_peername) >= 4
                and isinstance(raw_peername[2], int)
                and isinstance(raw_peername[3], int)
            ):
                peername = (host, port, raw_peername[2], raw_peername[3])
            else:
                peername = (host, port)

        route = self._app.route(header.target.path)
        if route is None:
            self._h3.send_headers(
                stream_id=event.stream_id,
                headers=[(b":status", b"404")],
                end_stream=True,
            )
            self.transmit()
            return

        session_info = WebTransportSessionInfo(
            session_id=event.stream_id,
            path=header.target,
            client=WebTransportClientInfo.from_peername(peername),
        )

        try:
            handler = route.handler_factory(session=session_info, **route.kwargs)
        except Exception:
            log.exception("创建处理器失败: path=%s", header.target.path)
            self._h3.send_headers(
                stream_id=event.stream_id,
                headers=[(b":status", b"500")],
                end_stream=True,
            )
            self.transmit()
            return

        session = WebTransportSession(
            h3=self._h3,
            quic=self._quic,
            session_info=session_info,
            handler=handler,
            transmit=self.transmit,
        )
        self._sessions[event.stream_id] = session
        asyncio.create_task(self._run_session(session))

    async def _run_session(self, session: WebTransportSession) -> None:
        try:
            await session.run()
        finally:
            self._sessions.pop(session.session_id, None)
