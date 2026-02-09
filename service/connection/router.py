import logging
from typing import Optional


from service.connection.dataclass import RouteInfo
from service.connection.handler import HandlerFactory


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
        log.info(f"已安排 {path} 端点")

    def route(self, path: str) -> Optional[RouteInfo]:
        """根据路径查找 handler"""
        return self._routes.get(path)
