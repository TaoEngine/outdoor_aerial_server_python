import logging

from service.connection.handler import WebTransportHandler, WebTransportStream
from service.connection.session import WebTransportSessionInfo
from service.controller import FetchService

log = logging.getLogger(__name__)


class BroadcastHandler(WebTransportHandler):
    def __init__(
        self,
        session: WebTransportSessionInfo,
        fetch_service: FetchService | None = None,
    ) -> None:
        super().__init__(session=session)
        # 依赖通过事件总线注入，避免直接创建采集服务实例
        self.__fetch = fetch_service
        self.__stream: WebTransportStream | None = None

    async def on_session_ready(self) -> None:
        if self.__fetch is None:
            log.warning("广播会话缺少采集服务依赖，已拒绝建立")
            self.close_session(error=True, reason="采集服务未初始化")
            return
        self.__stream = await self.create_stream(bidirectional=False)

        async def push(data: bytes) -> None:
            if self.__stream is None or self.__stream.closed:
                return
            await self.__stream.write(data)

        self.__fetch.subscribe(self.__stream.stream_id, push)

    async def on_session_closed(self, error: bool, reason: str | None) -> None:
        if self.__stream is not None and self.__fetch is not None:
            self.__fetch.unsubscribe(self.__stream.stream_id)
            self.__stream = None

