import asyncio
from plugin import hook_plugin


async def run_broadcast(pm, stop: asyncio.Event):
    """广播任务"""
    q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=128)

    async def producer():
        """从调谐器中采集广播作为生产者"""
        while not stop.is_set():
            for payload in await hook_plugin(pm, "capture"):
                if isinstance(payload, bytes):
                    await q.put(payload)

    async def consumer():
        """将广播发往作为消费者的客户端"""
        while not stop.is_set():
            payload = await q.get()
            await hook_plugin(pm, "entrypoint_broadcast", payload=payload)

    await asyncio.gather(producer(), consumer())
