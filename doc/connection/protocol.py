"""WebTransport 协议适配层文档。

该模块负责接收 QUIC/H3 事件，并驱动 WebTransportSession 的创建与事件分发。
"""

from typing import Any

from doc.connection.router import WebTransportRouter
from doc.connection.session import WebTransportSession


class WebTransportProtocol:
    """WebTransport 的协议处理入口。"""

    def __init__(self, *args, app: WebTransportRouter, **kwargs) -> None:
        """绑定路由器并初始化协议状态。"""

    def quic_event_received(self, event: Any) -> None:
        """接收 QUIC 事件并转为 H3/WebTransport 事件处理。"""

    def _handle_h3_event(self, event: Any) -> None:
        """分发 H3 层事件到会话或路由处理。"""

    def _handle_headers(self, event: Any) -> None:
        """处理 CONNECT/WebTransport 头部并创建会话。"""

    async def _run_session(self, session: WebTransportSession) -> None:
        """运行单个 WebTransport 会话并在结束后清理。"""
