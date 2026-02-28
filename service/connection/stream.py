import asyncio
from dataclasses import dataclass

from service.connection.interface import StreamSendFn, TransmitFn


@dataclass(frozen=True)
class WebTransportStreamConfig:
    """WebTransport 管道配置"""

    stream_id: int
    """客户端的 ID"""

    bidirectional: bool
    """指定单向流还是双向流"""

    readable: bool
    """管道是否可读"""

    writeable: bool
    """管道是否可写"""

    queue: int = 16
    """基于asyncio的queue最大容量"""


class WebTransportStream:
    """WebTransport 管道"""

    def __init__(
        self,
        config: WebTransportStreamConfig,
        send_stream_data: StreamSendFn,
        transmit: TransmitFn,
    ) -> None:
        self.__config = config
        """管道的配置"""

        self.__closed = False
        """管道是否关闭"""

        self.__queue: asyncio.Queue[tuple[bytes, bool]] = asyncio.Queue(
            maxsize=self.__config.queue
        )
        """管道需要处理的数据队列"""

        self._send_stream_data = send_stream_data
        self._transmit = transmit

    @property
    def stream_id(self) -> int:
        """管道要处理的流 ID"""
        return self.__config.stream_id

    @property
    def bidirectional(self) -> bool:
        """管道是单向还是双向"""
        return self.__config.bidirectional

    @property
    def readable(self) -> bool:
        """管道是否可读"""
        return self.__config.readable

    @property
    def writeable(self) -> bool:
        """管道是否可写"""
        return self.__config.writeable

    @property
    def closed(self) -> bool:
        """管道是否关闭"""
        return self.__closed

    async def read(self) -> bytes:
        """从管道内读取数据"""
        if not self.readable:
            raise RuntimeError(f"管道 {self.stream_id} 不可读取")

        if self.__closed and self.__queue.empty():
            raise RuntimeError(f"管道 {self.stream_id} 已被关闭")

        data, end_stream = await self.__queue.get()
        if end_stream:
            self.__closed = True
        return data

    async def write(self, data: bytes, end_stream: bool = False) -> None:
        """向管道内写入数据"""
        if not self.writeable:
            raise RuntimeError(f"管道 {self.stream_id} 不可写入")

        self._send_stream_data(self.stream_id, data, end_stream)
        if end_stream:
            self.__closed = True
        self._transmit()

    def _feed(self, data: bytes, end_stream: bool) -> None:
        """内部方法 将xxx接收到的数据塞入管道"""
        if self.__closed:
            return
        try:
            self.__queue.put_nowait((data, end_stream))
        except asyncio.QueueFull:
            if end_stream:
                self.__closed = True

    def close(self) -> None:
        """关闭管道"""
        if self.__closed:
            return
        self.__closed = True

        try:
            # 发送终止数据命令
            self.__queue.put_nowait((b"", True))
        except asyncio.QueueFull:
            pass
