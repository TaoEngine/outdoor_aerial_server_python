import asyncio
from typing import Awaitable, Callable
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import DatagramReceived, WebTransportStreamDataReceived
from starlette.types import Scope, Message, Receive, Send


class WebTransportSession:
    """与客户端进行的单次 WebTransport 会话"""

    def __init__(
        self,
        connection: H3Connection,
        stream_id: int,
        scope: Scope,
        transmit: Callable[[], None],
    ) -> None:
        self.__connection: H3Connection = connection
        self.__stream_id: int = stream_id
        self.__scope: Scope = scope
        self.__transmit: Callable[[], None] = transmit
        self.__queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=10)
        self.__accepted: bool = False

    async def receive(self):
        return await self.__queue.get()

    async def send(self, message: Message):
        match message["type"]:
            case "webtransport.accept":
                self.__accepted = True
                self.__connection.send_headers(
                    stream_id=self.__stream_id,
                    headers=[
                        (b":status", b"200"),
                        (b"sec-webtransport-http3-draft", b"draft02"),
                        (b"server", b"aioquic/0.9"),
                    ],
                )
            case "webtransport.datagram.send":
                self.__connection.send_datagram(
                    stream_id=self.__stream_id,
                    data=message["data"],
                )
            case "webtransport.stream.open":
                # 由服务端创建 WebTransport 流（默认双向，需兼容后续双向/单向扩展）
                is_unidirectional = message.get("is_unidirectional", False)
                stream_id = self.__connection.create_webtransport_stream(
                    session_id=self.__stream_id,
                    is_unidirectional=is_unidirectional,
                )
                self.__queue.put_nowait(
                    {
                        "type": "webtransport.stream.opened",
                        "stream": stream_id,
                        "is_unidirectional": is_unidirectional,
                    }
                )
            case "webtransport.stream.send":
                self.__connection.send_data(
                    stream_id=message.get("stream", self.__stream_id),
                    data=message["data"],
                    end_stream=message.get("end_stream", False),
                )
            case "webtransport.close":
                self.__connection.send_data(
                    stream_id=self.__stream_id,
                    data=b"",
                    end_stream=True,
                )
        self.__transmit()

    async def run_asgi(self, app: Callable[[Scope, Receive, Send], Awaitable[None]]):
        await self.__queue.put({"type": "webtransport.connect"})
        try:
            await app(self.__scope, self.receive, self.send)
        except Exception:
            pass
        finally:
            if not self.__accepted:
                self.__connection.send_headers(
                    stream_id=self.__stream_id, headers=[(b":status", b"403")]
                )
            else:
                self.__connection.send_data(
                    stream_id=self.__stream_id, data=b"", end_stream=True
                )
            self.__transmit()

    def handle_event(self, event: DatagramReceived | WebTransportStreamDataReceived):
        if isinstance(event, DatagramReceived):
            self.__queue.put_nowait(
                {
                    "type": "webtransport.datagram.receive",
                    "data": event.data,
                }
            )

        elif isinstance(event, WebTransportStreamDataReceived):
            self.__queue.put_nowait(
                {
                    "type": "webtransport.stream.receive",
                    "data": event.data,
                    "stream": event.stream_id,
                    "end_stream": event.stream_ended,
                }
            )
