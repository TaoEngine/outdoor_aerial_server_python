from pluggy import PluginManager


async def init_tuner(pm: PluginManager) -> None:
    return await pm.hook.init_tuner()


async def dispose_tuner(pm: PluginManager) -> None:
    return await pm.hook.dispose_tuner()


async def start_tuner(pm: PluginManager) -> None:
    return await pm.hook.start_tuner()