from __future__ import annotations

import logging

from event.bus import EventBus, ServiceContext
from service.controller import CaptureConfig, start_fetch_service

log = logging.getLogger(__name__)


def register_controller_service(bus: EventBus, config: CaptureConfig) -> None:
    """注册广播采集服务到事件总线。"""

    async def on_startup(_: EventBus, services: ServiceContext) -> None:
        log.info("准备初始化广播采集服务")
        services.controller = await start_fetch_service(config=config)
        log.info("广播采集服务已启动")

    def on_shutdown(_: EventBus, services: ServiceContext) -> None:
        if services.controller is None:
            return
        services.controller.stop()
        services.controller = None
        log.info("广播采集服务已停止")

    bus.startup.connect(on_startup, weak=False)
    bus.shutdown.connect(on_shutdown, weak=False)
