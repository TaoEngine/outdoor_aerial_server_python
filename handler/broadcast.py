from service.connection.handler import WebTransportHandler, WebTransportStream
from service.controller import FetchService


class BroadcastHandler(WebTransportHandler):
    def __init__(self, session_id: int, **kwargs) -> None:
        super().__init__(session_id=session_id, **kwargs)
        self._fetch = FetchService()
        self._stream: WebTransportStream | None = None

    async def on_session_ready(self) -> None:
        self._stream = await self.create_stream(bidirectional=False)

        async def push(data: bytes) -> None:
            if self._stream is None or self._stream.closed:
                return
            await self._stream.write(data)

        self._fetch.subscribe(self._stream.stream_id, push)

    async def on_session_closed(self, close_code: int, reason: str) -> None:
        if self._stream is not None:
            self._fetch.unsubscribe(self._stream.stream_id)
            self._stream = None
