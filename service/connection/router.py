import logging
from dataclasses import dataclass
from typing import Optional

from service.connection.types import HandlerFactory


@dataclass(frozen=True)
class RouteInfo:
    """WebTransport 路由注册项。"""

    handler_factory: "HandlerFactory"
    """处理器工厂，用于为每个会话构建处理器实例。"""

    kwargs: dict[str, object]
    """传给处理器工厂的额外参数。"""


log = logging.getLogger(__name__)


class WebTransportRouter:
    """WebTransport 的路由分发器"""

    def __init__(self) -> None:
        self._routes: dict[str, RouteInfo] = {}

    def add_route(self, path: str, handler_factory: HandlerFactory, **kwargs) -> None:
        """注册 WebTransport 路由"""
        self._routes[path] = RouteInfo(
            handler_factory=handler_factory,
            kwargs=kwargs,
        )
        log.info(f"已注册 {path} 路由端点")

    def route(self, path: str) -> Optional[RouteInfo]:
        """根据路径查找 handler"""
        return self._routes.get(path)
