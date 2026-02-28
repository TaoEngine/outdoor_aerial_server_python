from abc import ABC, abstractmethod

from service.connection.session import WebTransportSessionContext, WebTransportSessionInfo
from service.connection.stream import WebTransportStream


class WebTransportHandler(ABC):
    """供 WebTransport 端点处理业务的抽象"""

    def __init__(self, session: WebTransportSessionInfo) -> None:
        """绑定会话基本信息与路由参数"""
        # TODO 这里的Args需要变动
        self.__session: WebTransportSessionInfo = session
        self.__context: WebTransportSessionContext | None = None

    def bind_context(self, context: WebTransportSessionContext) -> None:
        """绑定会话上下文，供处理器发起任一操作"""
        # TODO 这里的Args需要变动
        self.__context = context

    def __get_context(self) -> WebTransportSessionContext:
        """获取已绑定的会话上下文"""
        if self.__context is None:
            path: str = self.__session.path.path
            # TODO 错误信息意义不明
            raise RuntimeError(f"位于 {path} 路径的业务处理器")
        return self.__context

    @abstractmethod
    async def on_session_ready(self) -> None:
        """会话已建立并可用时触发"""

    @abstractmethod
    async def on_session_closed(self, error: bool, reason: str | None) -> None:
        """会话关闭时触发

        Args:
            error (bool): 是否因为故障而关闭会话
            reason (str | None): 关闭会话的理由
        """

    async def on_stream_unidirectional(self, stream: WebTransportStream) -> None:
        """客户端请求创建单向流时触发

        Args:
            stream (WebTransportStream): 连接到客户端的 WebTransport 管道
        """

    async def on_stream_bidirectional(self, stream: WebTransportStream) -> None:
        """客户端请求创建双向流时触发

        Args:
            stream (WebTransportStream): 连接到客户端的 WebTransport 管道
        """

    async def on_datagram(self, data: bytes) -> None:
        """收到客户端的数据报时触发
        Args:
            data (bytes): 接收到的数据报
        """

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        """由服务端的处理器主动创建流
        Args:
            bidirectional (bool): 指定单向流 `(False)` 还是双向流 `(True)`

        Returns:
            WebTransportStream: 返回一个设置好的 WebTransport 管道
        """
        context = self.__get_context()
        return await context.create_stream(bidirectional=bidirectional)

    def send_datagram(self, data: bytes) -> None:
        """由服务端的处理器主动发送数据报
        
        Args:
            data (bytes): 需发送的数据报
        """
        context = self.__get_context()
        context.send_datagram(data)

    def close_session(self, error: bool = False, reason: str | None = None) -> None:
        """由服务端的处理器主动关闭会话
        
        Args:
            error (bool): 是否因为故障而关闭会话
            reason (str | None): 关闭会话的理由
        """
        context = self.__get_context()
        context.close_session(error, reason)
