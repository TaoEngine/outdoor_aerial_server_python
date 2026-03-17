import logging
from asyncio import Event, Queue, TaskGroup

from pluggy import PluginManager

from plugin.interface import distribute_broadcast

log = logging.getLogger(__name__)


async def run_broadcast(
    pm: PluginManager,
    event: Event,
    maxsize: int = 512,
) -> None:
    """执行广播任务

    Args:
        pm (PluginManager): 插件服务
        event (Event): 控制该任务的启停
        maxsize (int): 广播缓存最大大小
    """
    queue: Queue[bytes] = Queue(maxsize)

    async def producer():
        """从调谐器中采集广播作为生产者"""
        while not event.is_set():
            for payload in await capture_broadcast:
                if isinstance(payload, bytes):
                    await queue.put(payload)

    async def consumer():
        """将广播发往作为消费者的客户端"""
        await distribute_broadcast(pm, queue)

    try:
        log.info("广播分发服务已启动")
        async with TaskGroup() as group:
            group.create_task(producer())
            group.create_task(consumer())
    finally:
        event.set()
        log.info("广播分发服务已终止")
