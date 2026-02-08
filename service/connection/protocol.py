import asyncio
from typing import Optional

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

from service.connection.app import WebTransportApp
from service.connection.enum import H3Method, H3Protocol
from service.connection.session import WebTransportSession
from service.connection.dataclass import HeaderInfo, SessionInfo


class WebTransportProtocol(QuicConnectionProtocol):
    def __init__(self, *args, app=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._h3: Optional[H3Connection] = None
        self._app: Optional[WebTransportApp] = app
        self._sessions: dict[int, WebTransportSession] = {}
        """一个 ID 对应一个 Session 的列表"""

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated):
            self._h3 = H3Connection(self._quic, enable_webtransport=True)
        elif isinstance(event, ConnectionTerminated):
            for session in self._sessions.values():
                session.handle_connection_terminated(
                    code=event.error_code,
                    reason=event.reason_phrase,
                )

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
                session.handle_stream_event(event)

        elif isinstance(event, DatagramReceived):
            # 数据报事件：stream_id 就是 session_id
            session = self._sessions.get(event.stream_id)
            if session is not None:
                session.handle_datagram(event)

        elif isinstance(event, DataReceived):
            session = self._sessions.get(event.stream_id)
            if session is not None:
                session.handle_session_data(event)

    def _handle_headers(self, event: HeadersReceived) -> None:
        header = HeaderInfo.from_header(event.headers)

        if (
            header.method != H3Method.CONNECT
            or header.protocol != H3Protocol.WEBTRANSPORT
        ):
            return
        if self._h3 is None or self._app is None:
            return

        client_addr = (
            self._transport.get_extra_info("peername") if self._transport else None
        )

        route = self._app.route(header.path.path)
        if route is None:
            self._h3.send_headers(
                stream_id=event.stream_id,
                headers=[(b":status", b"404")],
                end_stream=True,
            )
            self.transmit()
            return

        session_info = SessionInfo(
            session_id=event.stream_id,
            path=header.path.path,
            query_string=header.path.query.encode(),
            headers=event.headers,
            client=client_addr,
        )

        handler = route.handler_factory(
            session_id=event.stream_id,
            session_info=session_info,
            **route.kwargs,
        )

        session = WebTransportSession(
            h3=self._h3,
            quic=self._quic,
            session_id=event.stream_id,
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
