import asyncio

from plugin import build_plugin_manager, hook_plugin
from .run_broadcast import run_broadcast


async def start():
    pm = build_plugin_manager()
    await asyncio.gather(
        hook_plugin(pm, "init_connection"),
        hook_plugin(pm, "init_database"),
        hook_plugin(pm, "init_repository"),
        hook_plugin(pm, "init_tuner"),
    )
    stop = asyncio.Event()
    asyncio.create_task(run_broadcast(pm, stop))
    await stop.wait()
