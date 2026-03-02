from __future__ import annotations

import logging
from typing import Any

from event.bus import EventBus, ServiceContext
from service.database import create_database_service

log = logging.getLogger(__name__)


def register_database_service(
    bus: EventBus,
    plugin_name: str = "sqlite",
    **backend_options: Any,
) -> None:
    """注册数据库服务到事件总线。"""

    async def on_startup(_: EventBus, services: ServiceContext) -> None:
        log.info("准备初始化数据库服务")
        service = await create_database_service(
            plugin_name=plugin_name,
            **backend_options,
        )
        await service.initialize()
        services.database = service
        log.info("数据库服务已完成初始化")

    def on_shutdown(_: EventBus, services: ServiceContext) -> None:
        if services.database is None:
            return
        services.database = None
        log.info("数据库服务已停止（当前无显式关闭接口）")

    bus.startup.connect(on_startup, weak=False)
    bus.shutdown.connect(on_shutdown, weak=False)
