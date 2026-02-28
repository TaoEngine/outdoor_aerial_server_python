"""WebTransport 会话文档。

该模块描述单个 WebTransport 会话的生命周期、流管理与事件分发方式。
"""

from typing import Any

from doc.connection.handler import WebTransportHandler
from doc.connection.interface.dataclass import SessionInfo
from doc.connection.stream import WebTransportStream


class WebTransportSession:
    """单个 WebTransport 会话，绑定一个处理器实例。"""

    def __init__(
        self,
        h3: Any,
        quic: Any,
        session_id: int,
        session_info: SessionInfo,
        handler: WebTransportHandler,
        transmit: Any,
    ) -> None:
        """绑定连接组件、会话信息与处理器。"""

    @property
    def session_id(self) -> int: # type: ignore
        """当前会话 ID。"""

    async def run(self) -> None:
        """启动会话并等待关闭。"""

    async def create_stream(self, bidirectional: bool = True) -> WebTransportStream: # type: ignore
        """由会话创建子流。"""

    def send_datagram(self, data: bytes) -> None:
        """通过会话发送数据报。"""

    def close_session(self, code: int = 0, reason: str = "") -> None:
        """关闭会话并可携带关闭原因。"""

    def handle_stream_event(self, event: Any) -> None:
        """处理来自子流的数据事件并分发给处理器。"""

    def handle_datagram(self, event: Any) -> None:
        """处理数据报事件并分发给处理器。"""

    def handle_session_data(self, event: Any) -> None:
        """处理会话级别的数据事件。"""

    def handle_connection_terminated(self, code: int, reason: str) -> None:
        """处理底层连接终止事件。"""
