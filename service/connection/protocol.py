import asyncio
from typing import Awaitable, Callable, Optional
from urllib.parse import urlsplit

from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import (
    DatagramReceived,
    H3Event,
    HeadersReceived,
    WebTransportStreamDataReceived,
)
from aioquic.quic.events import ProtocolNegotiated, QuicEvent
from starlette.types import Receive, Scope, Send

from service.connection.session import WebTransportSession
from service.connection.type import H3Header

ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class WebTransportProtocol(QuicConnectionProtocol):
    def __init__(self, *args, app: ASGIApp | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__h3: Optional[H3Connection] = None
        self.__app: ASGIApp | None = app
        self.__sessions: dict[int, WebTransportSession] = dict()

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated):
            # 与客户端握手成功，确定建立 HTTP/3 连接
            self.__h3 = H3Connection(self._quic, enable_webtransport=True)

        if self.__h3:
            # TODO 这是做什么的
            for h3_event in self.__h3.handle_event(event):
                self.__handle_event(h3_event)

    def __handle_event(self, event: H3Event) -> None:
        if isinstance(event, HeadersReceived):
            # 处理头部
            header = H3Header.from_header(event.headers)

            if header.method == "CONNECT" and header.protocol == "webtransport":
                path = header.path or "/"
                parts = urlsplit(path)
                client_addr = (
                    self._transport.get_extra_info("peername")
                    if self._transport
                    else None
                )

                scope: Scope = {
                    "type": "webtransport",
                    "path": parts.path,
                    "query_string": parts.query.encode(),
                    "headers": event.headers,
                    "client": client_addr,
                    "stream_id": event.stream_id,
                }

                if self.__h3 is None or self.__app is None:
                    return

                session = WebTransportSession(
                    connection=self.__h3,
                    stream_id=event.stream_id,
                    scope=scope,
                    transmit=self.transmit
                )
                self.__sessions[event.stream_id] = session

                asyncio.create_task(session.run_asgi(self.__app))

        elif isinstance(event, (DatagramReceived, WebTransportStreamDataReceived)):
            session = self.__sessions.get(event.stream_id)
            if session:
                session.handle_event(event)
