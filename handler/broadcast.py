import logging

from aioquic.h3.connection import H3Connection
from aioquic.h3.events import WebTransportStreamDataReceived, HeadersReceived

from service.capture import CaptureService

log = logging.getLogger(__name__)


class BroadcastHandler:
    def __init__(self, connection: H3Connection, capture: CaptureService):
        self.__capture: CaptureService = capture
        """采集广播服务"""

        self.__connection: H3Connection = connection
        """WebTransport 客户端"""

    def handle(self, event: HeadersReceived | WebTransportStreamDataReceived) -> None:
        """处理 WebTransport 的生命周期"""
        if isinstance(event, HeadersReceived):
            self.__connect(event.stream_id)
        elif isinstance(event, WebTransportStreamDataReceived):
            if event.stream_ended:
                self.__close(event.stream_id)

    def __connect(self, id: int) -> None:
        """通过 WebTransport 提供服务"""

        async def broadcast(data: bytes) -> None:
            self.__connection.send_data(id, data, end_stream=False)

        self.__capture.subscribe(id, broadcast)

    def __close(self, id: int) -> None:
        """关闭 WebTransport 服务"""
        self.__capture.unsubscribe(id)

    def cleanup(self) -> None:
        """清理所有广播流"""
        pass
