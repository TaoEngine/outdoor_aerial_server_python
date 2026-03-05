import logging

import trio
from pluggy import PluginManager

from plugin import hook_plugin

log = logging.getLogger(__name__)


async def run_broadcast(
    pm: PluginManager,
    event: trio.Event,
    buffer_size: int = 512,
) -> None:
    """执行广播任务

    Args:
        pm (PluginManager): 插件服务
        event (Event): 控制该任务的启停
        maxsize (int): 广播缓存最大大小
    """
    send, recv = trio.open_memory_channel(buffer_size)

    async def producer():
        """从调谐器中采集广播作为生产者"""
        while not event.is_set():
            for payload in await hook_plugin(pm, "capture"):
                if isinstance(payload, bytes):
                    await send.send(payload)

    async def consumer():
        """将广播发往作为消费者的客户端"""
        while not event.is_set():
            payload = await recv.receive()
            await hook_plugin(pm, "entrypoint_broadcast", payload=payload)

    try:
        log.info("广播分发服务以启动")
        async with trio.open_nursery() as nursery:
            nursery.start_soon(producer)
            nursery.start_soon(consumer)
    finally:
        event.set()
        log.info("广播分发服务已终止")
