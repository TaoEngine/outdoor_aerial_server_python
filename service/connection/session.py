from __future__ import annotations

import asyncio
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

from service.connection.handler import WebTransportHandler, WebTransportStream
from service.connection.interface.dataclass import SessionInfo

log = logging.getLogger(__name__)


class WebTransportSession:
    """Single WebTransport session bound to a handler instance."""

    def __init__(
        self,
        h3: H3Connection,
        quic: QuicConnection,
        session_id: int,
        session_info: SessionInfo,
        handler: WebTransportHandler,
        transmit: Callable[[], None],
    ) -> None:
        self._h3 = h3
        self._quic = quic
        self._session_id = session_id
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
        return self._session_id

    async def run(self) -> None:
        self._accept()
        try:
            await self._handler.on_session_ready()
            await self._closed_event.wait()
        except Exception as exc:
            log.warning("WebTransport handler error: %s", exc)
            self._mark_closed(code=1, reason="handler error", send=True)
        finally:
            await self._finalize()

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        if self._closed:
            raise RuntimeError("Session is closed.")
        is_unidirectional = not bidirectional
        stream_id = self._h3.create_webtransport_stream(
            session_id=self._session_id,
            is_unidirectional=is_unidirectional,
        )
        stream = WebTransportStream(
            stream_id,
            is_unidirectional=is_unidirectional,
            can_read=bidirectional,
            can_write=True,
            send_stream_data=self._quic.send_stream_data,
            transmit=self._transmit,
        )
        self._streams[stream_id] = stream
        return stream

    def send_datagram(self, data: bytes) -> None:
        if self._closed:
            return
        self._h3.send_datagram(stream_id=self._session_id, data=data)
        self._transmit()

    def close_session(self, code: int = 0, reason: str = "") -> None:
        self._mark_closed(code=code, reason=reason, send=True)

    def handle_stream_event(self, event: WebTransportStreamDataReceived) -> None:
        stream_id = event.stream_id
        stream = self._streams.get(stream_id)
        is_uni = stream_is_unidirectional(stream_id)
        is_client = stream_is_client_initiated(stream_id)

        if stream is None:
            stream = WebTransportStream(
                stream_id,
                is_unidirectional=is_uni,
                can_read=(not is_uni) or is_client,
                can_write=(not is_uni) or (not is_client),
                send_stream_data=self._quic.send_stream_data,
                transmit=self._transmit,
            )
            self._streams[stream_id] = stream
            if is_client:
                if is_uni:
                    self._spawn_task(self._handler.on_stream_unidirectional(stream))
                else:
                    self._spawn_task(self._handler.on_stream_bidirectional(stream))

        if stream.can_read:
            stream.feed_data(event.data, event.stream_ended)

    def handle_datagram(self, event: DatagramReceived) -> None:
        self._spawn_task(self._handler.on_datagram(event.data))

    def handle_session_data(self, event: DataReceived) -> None:
        if event.stream_ended:
            self._mark_closed(code=0, reason="client closed", send=False)

    def handle_connection_terminated(self, code: int, reason: str) -> None:
        self._mark_closed(code=code, reason=reason, send=False)

    def _accept(self) -> None:
        if self._accepted:
            return
        self._accepted = True
        self._h3.send_headers(
            stream_id=self._session_id,
            headers=[(b":status", b"200")],
            end_stream=False,
        )
        self._transmit()

    def _mark_closed(self, code: int, reason: str, send: bool) -> None:
        if self._closed:
            return
        self._closed = True
        self._close_code = code
        self._close_reason = reason
        if send:
            self._h3.send_data(
                stream_id=self._session_id,
                data=b"",
                end_stream=True,
            )
            self._transmit()
        self._closed_event.set()

    async def _finalize(self) -> None:
        for stream in self._streams.values():
            stream.close()
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        try:
            await self._handler.on_session_closed(
                close_code=self._close_code,
                reason=self._close_reason,
            )
        except Exception as exc:
            log.warning("WebTransport close handler error: %s", exc)

    def _spawn_task(self, coro: Coroutine[Any, Any, None]) -> None:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._handle_task_done)

    def _handle_task_done(self, task: asyncio.Task[None]) -> None:
        self._tasks.discard(task)
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            log.warning("WebTransport handler task error: %s", exc)
