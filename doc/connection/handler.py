"""WebTransport 处理器接口文档。

该文件描述 WebTransport 会话处理器的职责、生命周期与回调接口。
实现类通常只关心业务逻辑，不需要处理底层 QUIC/H3 事件细节。
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Callable, Protocol

from doc.connection.stream import WebTransportStream

if TYPE_CHECKING:
    from doc.connection.interface.dataclass import SessionInfo


class WebTransportSessionContext(Protocol):
    """处理器可调用的会话上下文能力。"""

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream: # type: ignore
        """创建子流。"""

    def send_datagram(self, data: bytes) -> None:
        """发送数据报。"""

    def close_session(self, code: int = 0, reason: str = "") -> None:
        """主动关闭会话。"""


class WebTransportHandler(ABC):
    """WebTransport 会话的业务处理器抽象。"""

    def __init__(
        self,
        session_id: int,
        session_info: SessionInfo | None = None,
        **kwargs,
    ) -> None:
        """绑定会话基本信息与路由参数。"""

    def bind_context(self, context: WebTransportSessionContext) -> None:
        """绑定会话上下文，供处理器发起写入或关闭操作。"""

    async def on_session_ready(self) -> None:
        """会话已建立并可读写时触发。"""

    async def on_session_closed(self, close_code: int, reason: str) -> None:
        """会话关闭后回调。"""

    async def on_stream_unidirectional(self, stream: WebTransportStream) -> None:
        """对端创建单向流时回调。"""

    async def on_stream_bidirectional(self, stream: WebTransportStream) -> None:
        """对端创建双向流时回调。"""

    async def on_datagram(self, data: bytes) -> None:
        """收到数据报时回调。"""

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream: # type: ignore
        """由处理器主动创建子流。"""

    def send_datagram(self, data: bytes) -> None:
        """由处理器主动发送数据报。"""

    def close_session(self, code: int = 0, reason: str = "") -> None:
        """由处理器主动关闭会话。"""


HandlerFactory = Callable[..., WebTransportHandler]
