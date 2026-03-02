from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from blinker import Namespace, Signal

if TYPE_CHECKING:
    from aioquic.asyncio.server import QuicServer

    from service.controller.fetch import FetchService
    from service.database.service import DatabaseService

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ServiceContext:
    """事件总线维护的服务实例集合。"""

    connection: "QuicServer | None" = None
    """WebTransport 连接服务实例。"""

    controller: "FetchService | None" = None
    """广播信号采集分发服务实例。"""

    database: "DatabaseService | None" = None
    """数据库服务实例。"""


class EventBus:
    """基于 blinker 的服务事件总线。"""

    def __init__(self) -> None:
        self._signals = Namespace()
        self.startup: Signal = self._signals.signal("startup")
        self.shutdown: Signal = self._signals.signal("shutdown")
        self.services = ServiceContext()

    async def emit(self, signal: Signal, **payload: Any) -> None:
        """触发事件并等待异步处理器完成。"""
        for receiver in list(signal.receivers_for(self)):
            receiver_name = getattr(receiver, "__name__", repr(receiver))
            try:
                result = receiver(self, **payload)
            except Exception:
                log.exception(f"事件处理器执行异常: {receiver_name}")
                continue
            if inspect.isawaitable(result):
                try:
                    await result
                except Exception:
                    log.exception(f"事件处理器异步执行异常: {receiver_name}")

    async def startup_services(self) -> ServiceContext:
        """触发服务初始化事件。"""
        log.info("事件总线开始初始化服务")
        await self.emit(self.startup, services=self.services)
        log.info("事件总线已完成服务初始化")
        return self.services

    async def shutdown_services(self) -> None:
        """触发服务停止事件。"""
        log.info("事件总线开始停止服务")
        await self.emit(self.shutdown, services=self.services)
        log.info("事件总线已完成服务停止")
