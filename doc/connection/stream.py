"""WebTransport 流接口文档。

该文件描述 WebTransport 子流的语义与读写行为，用于理解流的生命周期。
"""


class WebTransportStream:
    """WebTransport 子流抽象描述。"""

    @property
    def stream_id(self) -> int:  # type: ignore
        """流的唯一标识符。"""

    @property
    def is_unidirectional(self) -> bool:  # type: ignore
        """是否为单向流。"""

    @property
    def can_read(self) -> bool:  # type: ignore
        """当前流是否允许读取。"""

    @property
    def can_write(self) -> bool:  # type: ignore
        """当前流是否允许写入。"""

    @property
    def closed(self) -> bool:  # type: ignore
        """流是否已关闭。"""

    async def read(self) -> bytes:  # type: ignore
        """读取流数据。

        返回读取到的字节；当流关闭且无数据时通常返回空字节。
        """

    async def write(self, data: bytes, end_stream: bool = False) -> None:
        """向流写入数据。

        end_stream 表示本次写入是否结束该流。
        """

    def feed_data(self, data: bytes, end_stream: bool) -> None:
        """投递来自底层的流数据到读取队列。"""

    def close(self) -> None:
        """关闭流并释放资源。"""
