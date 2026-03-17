from pluggy import PluginManager

from plugin.spec.multimodel import ModelConfig


async def init_multimodel(pm: PluginManager) -> None:
    return await pm.hook.init_multimodel()


async def dispose_multimodel(pm: PluginManager) -> None:
    return await pm.hook.dispose_multimodel()


async def configure_multimodel(pm: PluginManager, config: ModelConfig) -> None:
    return await pm.hook.configure_multimodel(config=config)


async def multimodel_request(pm: PluginManager) -> ...:
    return await pm.hook.multimodel_request()