import logging

import trio
from pluggy import PluginManager

from plugin import build_plugin_manager, call_plugin

from .run_broadcast import run_broadcast
from .process_episode import process_episode

log = logging.getLogger(__name__)


async def init_plugin(pm: PluginManager) -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(call_plugin, pm, "init_agent")
        nursery.start_soon(call_plugin, pm, "init_connection")
        nursery.start_soon(call_plugin, pm, "init_database")
        nursery.start_soon(call_plugin, pm, "init_repository")
        nursery.start_soon(call_plugin, pm, "init_tuner")
    log.info("已初始化所有服务")


async def dispose_plugin(pm: PluginManager) -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(call_plugin, pm, "dispose_agent")
        nursery.start_soon(call_plugin, pm, "dispose_connection")
        nursery.start_soon(call_plugin, pm, "dispose_database")
        nursery.start_soon(call_plugin, pm, "dispose_repository")
        nursery.start_soon(call_plugin, pm, "dispose_tuner")
    log.info("已卸载所有服务")


async def runtime():
    pm = build_plugin_manager()
    await init_plugin(pm)

    event = trio.Event()
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(run_broadcast, pm, event)
            nursery.start_soon(process_episode, pm)
    except KeyboardInterrupt:
        log.exception("服务被 Ctrl+C 终止运行")
    finally:
        await dispose_plugin(pm)
