from __future__ import annotations

import abc
import asyncio
from typing import Callable, Protocol

from service.connection.dataclass import SessionInfo


StreamSendFn = Callable[[int, bytes, bool], None]
TransmitFn = Callable[[], None]


class WebTransportStream:
    def __init__(
        self,
        stream_id: int,
        *,
        is_unidirectional: bool,
        can_read: bool,
        can_write: bool,
        send_stream_data: StreamSendFn,
        transmit: TransmitFn,
        queue_size: int = 16,
    ) -> None:
        self._stream_id = stream_id
        self._is_unidirectional = is_unidirectional
        self._can_read = can_read
        self._can_write = can_write
        self._send_stream_data = send_stream_data
        self._transmit = transmit
        self._queue: asyncio.Queue[tuple[bytes, bool]] = asyncio.Queue(
            maxsize=queue_size
        )
        self._closed = False

    @property
    def stream_id(self) -> int:
        return self._stream_id

    @property
    def is_unidirectional(self) -> bool:
        return self._is_unidirectional

    @property
    def can_read(self) -> bool:
        return self._can_read

    @property
    def can_write(self) -> bool:
        return self._can_write

    @property
    def closed(self) -> bool:
        return self._closed

    async def read(self) -> bytes:
        if not self._can_read:
            raise RuntimeError("Stream is not readable.")
        if self._closed and self._queue.empty():
            return b""
        data, end_stream = await self._queue.get()
        if end_stream:
            self._closed = True
        return data

    async def write(self, data: bytes, end_stream: bool = False) -> None:
        if not self._can_write:
            raise RuntimeError("Stream is not writable.")
        self._send_stream_data(self._stream_id, data, end_stream)
        if end_stream:
            self._closed = True
        self._transmit()

    def feed_data(self, data: bytes, end_stream: bool) -> None:
        if self._closed:
            return
        try:
            self._queue.put_nowait((data, end_stream))
        except asyncio.QueueFull:
            # Drop data if the application is too slow.
            if end_stream:
                self._closed = True

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._queue.put_nowait((b"", True))
        except asyncio.QueueFull:
            pass


class WebTransportSessionContext(Protocol):
    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        ...

    def send_datagram(self, data: bytes) -> None:
        ...

    def close_session(self, code: int = 0, reason: str = "") -> None:
        ...


class WebTransportHandler(abc.ABC):
    def __init__(
        self,
        session_id: int,
        session_info: SessionInfo | None = None,
        **kwargs,
    ) -> None:
        self.session_id = session_id
        self.session_info = session_info
        self.route_params = kwargs
        self._transport_context: WebTransportSessionContext | None = None

    def bind_context(self, context: WebTransportSessionContext) -> None:
        self._transport_context = context

    async def on_session_ready(self) -> None:
        pass

    async def on_session_closed(self, close_code: int, reason: str) -> None:
        pass

    async def on_stream_unidirectional(self, stream: WebTransportStream) -> None:
        pass

    async def on_stream_bidirectional(self, stream: WebTransportStream) -> None:
        pass

    async def on_datagram(self, data: bytes) -> None:
        pass

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        context = self._ensure_context()
        return await context.create_stream(bidirectional=bidirectional)

    def send_datagram(self, data: bytes) -> None:
        context = self._ensure_context()
        context.send_datagram(data)

    def close_session(self, code: int = 0, reason: str = "") -> None:
        context = self._ensure_context()
        context.close_session(code=code, reason=reason)

    def _ensure_context(self) -> WebTransportSessionContext:
        if self._transport_context is None:
            raise RuntimeError("WebTransport context is not bound yet.")
        return self._transport_context
