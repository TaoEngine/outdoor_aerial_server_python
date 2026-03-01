from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from service.connection.stream import WebTransportStream

if TYPE_CHECKING:
    from service.connection.session import WebTransportSessionInfo


class WebTransportSessionContext(Protocol):
    """处理器可调用的会话上下文能力。"""

    async def create_stream(self, bidirectional: bool) -> WebTransportStream:
        """由服务端主动创建 WebTransport 流。"""
        ...

    def send_datagram(self, data: bytes) -> None:
        """由服务端主动发送 WebTransport datagram。"""
        ...

    def close_session(self, error: bool, reason: str | None = None) -> None:
        """由服务端主动关闭会话。"""
        ...


class WebTransportHandler(ABC):
    """WebTransport 端点业务处理器抽象基类。"""

    def __init__(self, session: WebTransportSessionInfo) -> None:
        """保存会话元信息，等待绑定运行时上下文。"""
        self.__session = session
        self.__context: WebTransportSessionContext | None = None

    def bind_context(self, context: WebTransportSessionContext) -> None:
        """绑定会话上下文，供子类在回调中操作会话。"""
        self.__context = context

    def __get_context(self) -> WebTransportSessionContext:
        """获取已绑定的会话上下文。"""
        if self.__context is None:
            path: str = self.__session.path.path
            raise RuntimeError(f"{path} 处理器尚未绑定会话上下文")
        return self.__context

    @abstractmethod
    async def on_session_ready(self) -> None:
        """抽象回调：会话完成握手并可用时触发。"""

    @abstractmethod
    async def on_session_closed(self, error: bool, reason: str | None) -> None:
        """抽象回调：会话关闭后触发。"""

    async def on_stream_unidirectional(self, stream: WebTransportStream) -> None:
        """可选回调：客户端创建单向流时触发。"""

    async def on_stream_bidirectional(self, stream: WebTransportStream) -> None:
        """可选回调：客户端创建双向流时触发。"""

    async def on_datagram(self, data: bytes) -> None:
        """可选回调：收到客户端 datagram 时触发。"""

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream:
        """由处理器主动创建单向/双向流。"""
        context = self.__get_context()
        return await context.create_stream(bidirectional=bidirectional)

    def send_datagram(self, data: bytes) -> None:
        """由处理器主动发送 datagram。"""
        context = self.__get_context()
        context.send_datagram(data)

    def close_session(self, error: bool = False, reason: str | None = None) -> None:
        """由处理器主动关闭会话。"""
        context = self.__get_context()
        context.close_session(error, reason)
