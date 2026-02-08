import asyncio
from typing import Callable, Optional
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

from service.connection.session import WebTransportSession
from service.connection.type import H3Header

Handler = Callable


class WebTransportProtocol(QuicConnectionProtocol):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._h3: Optional[H3Connection] = None
        self._app = app
        # session_id -> WebTransportSession
        self._sessions: dict[int, WebTransportSession] = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated):
            self._h3 = H3Connection(self._quic, enable_webtransport=True)

        if self._h3 is not None:
            for h3_event in self._h3.handle_event(event):
                self._handle_h3_event(h3_event)
            self.transmit()

    def _handle_h3_event(self, event: H3Event) -> None:
        if isinstance(event, HeadersReceived):
            self._handle_headers(event)

        elif isinstance(event, WebTransportStreamDataReceived):
            # 子流事件：通过 event.session_id 找到所属会话
            session = self._sessions.get(event.session_id)
            if session is not None:
                session.handle_event(event)

        elif isinstance(event, DatagramReceived):
            # 数据报事件：stream_id 就是 session_id
            session = self._sessions.get(event.stream_id)
            if session is not None:
                session.handle_event(event)

    def _handle_headers(self, event: HeadersReceived) -> None:
        header = H3Header.from_header(event.headers)

        if header.method != "CONNECT" or header.protocol != "webtransport":
            return
        if self._h3 is None or self._app is None:
            return

        path = header.path or "/"
        parts = urlsplit(path)
        client_addr = (
            self._transport.get_extra_info("peername")
            if self._transport
            else None
        )

        scope = {
            "type": "webtransport",
            "path": parts.path,
            "query_string": parts.query.encode(),
            "headers": event.headers,
            "client": client_addr,
            "session_id": event.stream_id,
        }

        session = WebTransportSession(
            h3=self._h3,
            quic=self._quic,
            session_id=event.stream_id,
            scope=scope,
            transmit=self.transmit,
        )
        self._sessions[event.stream_id] = session

        handler = self._app.route(parts.path)
        if handler is not None:
            asyncio.create_task(self._run_session(session, handler))

    async def _run_session(self, session: WebTransportSession, handler) -> None:
        try:
            await session.run(handler)
        finally:
            self._sessions.pop(session.session_id, None)
