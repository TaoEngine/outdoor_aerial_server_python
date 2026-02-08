import asyncio
import logging
from typing import Callable

from aioquic.h3.connection import H3Connection
from aioquic.h3.events import DatagramReceived, WebTransportStreamDataReceived
from aioquic.quic.connection import QuicConnection

log = logging.getLogger(__name__)

# handler 收发消息的类型定义
# {
#     "type": "webtransport.connect"                          — 收：会话建立请求
#     "type": "webtransport.accept"                           — 发：接受会话
#     "type": "webtransport.close"                            — 收/发：会话关闭
#     "type": "webtransport.stream.open",
#         "is_unidirectional": bool                           — 发：请求创建流
#     "type": "webtransport.stream.opened",
#         "stream": int, "is_unidirectional": bool            — 收：流已创建
#     "type": "webtransport.stream.send",
#         "stream": int, "data": bytes                        — 发：向流写数据
#     "type": "webtransport.stream.receive",
#         "data": bytes, "stream": int, "end_stream": bool    — 收：流上收到数据
#     "type": "webtransport.datagram.send", "data": bytes     — 发：发送数据报
#     "type": "webtransport.datagram.receive", "data": bytes  — 收：收到数据报
# }

Message = dict


class WebTransportSession:
    """与客户端进行的单次 WebTransport 会话"""

    def __init__(
        self,
        h3: H3Connection,
        quic: QuicConnection,
        session_id: int,
        scope: dict,
        transmit: Callable[[], None],
    ) -> None:
        self._h3 = h3
        self._quic = quic
        self._session_id = session_id
        self._scope = scope
        self._transmit = transmit
        self._queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=16)
        self._accepted = False
        self._closed = False

    @property
    def session_id(self) -> int:
        return self._session_id

    async def receive(self) -> Message:
        """handler 调用：从队列中取出一条消息"""
        return await self._queue.get()

    async def send(self, message: Message) -> None:
        """handler 调用：向客户端发送消息"""
        msg_type: str = message["type"]

        if msg_type == "webtransport.accept":
            self._accepted = True
            self._h3.send_headers(
                stream_id=self._session_id,
                headers=[(b":status", b"200")],
                end_stream=False,
            )

        elif msg_type == "webtransport.stream.open":
            is_uni = message.get("is_unidirectional", False)
            stream_id = self._h3.create_webtransport_stream(
                session_id=self._session_id,
                is_unidirectional=is_uni,
            )
            # 将创建结果放回队列，让 handler 通过 receive() 拿到 stream_id
            self._queue.put_nowait(
                {
                    "type": "webtransport.stream.opened",
                    "stream": stream_id,
                    "is_unidirectional": is_uni,
                }
            )

        elif msg_type == "webtransport.stream.send":
            # WebTransport 子流必须用 QUIC 层直接发送原始数据
            self._quic.send_stream_data(
                stream_id=message["stream"],
                data=message["data"],
                end_stream=message.get("end_stream", False),
            )

        elif msg_type == "webtransport.datagram.send":
            self._h3.send_datagram(
                stream_id=self._session_id,
                data=message["data"],
            )

        elif msg_type == "webtransport.close":
            self._closed = True
            self._h3.send_data(
                stream_id=self._session_id,
                data=b"",
                end_stream=True,
            )

        self._transmit()

    def handle_event(self, event: DatagramReceived | WebTransportStreamDataReceived) -> None:
        """protocol 调用：将 H3 事件转为消息放入队列"""
        if isinstance(event, DatagramReceived):
            self._queue.put_nowait(
                {
                    "type": "webtransport.datagram.receive",
                    "data": event.data,
                }
            )
        elif isinstance(event, WebTransportStreamDataReceived):
            self._queue.put_nowait(
                {
                    "type": "webtransport.stream.receive",
                    "data": event.data,
                    "stream": event.stream_id,
                    "end_stream": event.stream_ended,
                }
            )

    async def run(self, handler) -> None:
        """启动 handler 协程，管理会话生命周期"""
        self._queue.put_nowait({"type": "webtransport.connect"})
        try:
            await handler(self._scope, self.receive, self.send)
        except Exception as e:
            log.warning(f"WebTransport handler 异常: {e}")
        finally:
            if not self._accepted:
                self._h3.send_headers(
                    stream_id=self._session_id,
                    headers=[(b":status", b"403")],
                )
            elif not self._closed:
                self._h3.send_data(
                    stream_id=self._session_id,
                    data=b"",
                    end_stream=True,
                )
            self._transmit()
