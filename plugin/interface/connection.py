from asyncio import Queue

from pluggy import PluginManager


async def init_connection(pm: PluginManager) -> None:
    return await pm.hook.init_connection()


async def dispose_connection(pm: PluginManager) -> None:
    return await pm.hook.dispose_connection()


async def distribute_broadcast(pm: PluginManager, payload: Queue[bytes]) -> None:
    return await pm.hook.entrypoint_broadcast(payload=payload)
