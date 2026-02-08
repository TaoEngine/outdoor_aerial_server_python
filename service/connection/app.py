import logging
from typing import Callable, Optional

log = logging.getLogger(__name__)


class WebTransportApp:
    """WebTransport 路由分发器"""

    def __init__(self) -> None:
        self._routes: dict[str, Callable] = {}

    def add_route(self, path: str, handler: Callable) -> None:
        """注册 WebTransport 路由"""
        self._routes[path] = handler
        log.info(f"已注册 WebTransport 端点: {path}")

    def route(self, path: str) -> Optional[Callable]:
        """根据路径查找 handler"""
        return self._routes.get(path)
