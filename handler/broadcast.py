from service.connection.handler import WebTransportHandler, WebTransportStream
from service.connection.session import WebTransportSessionInfo
from service.controller import FetchService


class BroadcastHandler(WebTransportHandler):
    def __init__(self, session: WebTransportSessionInfo) -> None:
        super().__init__(session=session)
        # TODO 在后期采用事件驱动而不是直接与FetchService绑定，以解耦
        self.__fetch = FetchService()
        self.__stream: WebTransportStream | None = None

    async def on_session_ready(self) -> None:
        self.__stream = await self.create_stream(bidirectional=False)

        async def push(data: bytes) -> None:
            if self.__stream is None or self.__stream.closed:
                return
            await self.__stream.write(data)

        self.__fetch.subscribe(self.__stream.stream_id, push)

    async def on_session_closed(self, error: bool, reason: str | None) -> None:
        if self.__stream is not None:
            self.__fetch.unsubscribe(self.__stream.stream_id)
            self.__stream = None

