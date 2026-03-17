from pluggy import PluginManager


async def init_repository(pm: PluginManager) -> None:
    return await pm.hook.init_repository()


async def dispose_repository(pm: PluginManager) -> None:
    return await pm.hook.dispose_repository()