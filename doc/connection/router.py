"""WebTransport 路由器文档。

该模块负责将路径映射到处理器工厂，供协议层创建会话时使用。
"""

from typing import Optional

from doc.connection.handler import HandlerFactory
from doc.connection.interface.dataclass import RouteInfo


class WebTransportRouter:
    """WebTransport 的路由分发器。"""

    def __init__(self) -> None:
        """初始化路由表。"""

    def add_route(self, path: str, handler_factory: HandlerFactory, **kwargs) -> None:
        """注册 WebTransport 路由。"""

    def route(self, path: str) -> Optional[RouteInfo]:
        """根据路径查找路由信息。"""
