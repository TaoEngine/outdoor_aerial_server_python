from __future__ import annotations

import logging
from dataclasses import dataclass, field
from socket import gaierror
from typing import Callable, Mapping, Sequence

from aioquic.asyncio.server import serve
from aioquic.quic.configuration import QuicConfiguration

from event.bus import EventBus, ServiceContext
from service.connection.protocol import WebTransportProtocol
from service.connection.router import WebTransportRouter
from service.connection.types import HandlerFactory

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ConnectionRoute:
    """连接服务的路由配置。"""

    path: str
    """路由路径。"""

    handler_factory: HandlerFactory
    """处理器工厂。"""

    kwargs: Mapping[str, object] = field(default_factory=dict)
    """额外参数。"""

    kwargs_factory: Callable[[ServiceContext], Mapping[str, object]] | None = None
    """根据服务上下文生成额外参数的工厂函数。"""


@dataclass(frozen=True, slots=True)
class ConnectionOptions:
    """连接服务启动参数。"""

    configuration: QuicConfiguration
    """QUIC 配置。"""

    host: str
    """监听主机名或 IP。"""

    port: int = 58908
    """监听端口。"""

    routes: Sequence[ConnectionRoute] = field(default_factory=tuple)
    """路由列表。"""


def register_connection_service(bus: EventBus, options: ConnectionOptions) -> None:
    """注册 WebTransport 连接服务到事件总线。"""

    async def on_startup(_: EventBus, services: ServiceContext) -> None:
        log.info("准备初始化连接服务")
        router = WebTransportRouter()
        for route in options.routes:
            kwargs: dict[str, object] = dict(route.kwargs)
            if route.kwargs_factory is not None:
                kwargs.update(route.kwargs_factory(services))
            router.add_route(route.path, route.handler_factory, **kwargs)

        try:
            server = await serve(
                host=options.host,
                port=options.port,
                configuration=options.configuration,
                create_protocol=lambda *args, **kwargs: WebTransportProtocol(
                    app=router,
                    *args,
                    **kwargs,
                ),
            )
        except gaierror:
            log.fatal(f"{options.host} 是个并不存在的域名")
            return
        except OSError:
            log.fatal(f"{options.host} 域名未与本机的 IP 绑定在一起")
            return

        services.connection = server
        log.info(f"连接服务已启动 host={options.host} port={options.port}")

    def on_shutdown(_: EventBus, services: ServiceContext) -> None:
        if services.connection is None:
            return
        services.connection.close()
        services.connection = None
        log.info("连接服务已停止")

    bus.startup.connect(on_startup, weak=False)
    bus.shutdown.connect(on_shutdown, weak=False)
