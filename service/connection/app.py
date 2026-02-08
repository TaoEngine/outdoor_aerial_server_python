import logging
from dataclasses import dataclass
from typing import Callable, Optional, Any

from service.connection.handler import WebTransportHandler

log = logging.getLogger(__name__)

HandlerFactory = Callable[..., WebTransportHandler]


@dataclass(frozen=True)
class WebTransportRoute:
    handler_factory: HandlerFactory
    kwargs: dict[str, Any]


class WebTransportApp:
    """WebTransport 路由分发器"""

    def __init__(self) -> None:
        self._routes: dict[str, WebTransportRoute] = {}

    def add_route(self, path: str, handler_factory: HandlerFactory, **kwargs) -> None:
        """注册 WebTransport 路由"""
        self._routes[path] = WebTransportRoute(
            handler_factory=handler_factory,
            kwargs=kwargs,
        )
        log.info(f"已注册 WebTransport 端点: {path}")

    def route(self, path: str) -> Optional[WebTransportRoute]:
        """根据路径查找 handler"""
        return self._routes.get(path)
