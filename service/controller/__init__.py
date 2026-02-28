"""与调谐器 HAT 进行交互的模块 包含控制与采集模块"""

import asyncio
import logging
from typing import Optional

from service.controller.dataclass import (
    CaptureChannel,
    CaptureConfig,
    CaptureDtype,
    CaptureSampleRate,
)
from service.controller.fetch import FetchService

__all__ = [
    "FetchService",
    "CaptureSampleRate",
    "CaptureChannel",
    "CaptureDtype",
    "CaptureConfig",
]

log = logging.getLogger(__name__)


async def start_fetch_service(config: CaptureConfig) -> Optional[FetchService]:
    """启动广播信号采集服务"""
    fetch_service = FetchService(config=config)
    asyncio.create_task(fetch_service.start())
    return fetch_service
