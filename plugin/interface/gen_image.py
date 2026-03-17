from pluggy import PluginManager


async def init_gen_image(pm: PluginManager) -> None:
    return await pm.hook.init_gen_image()


async def dispose_gen_image(pm: PluginManager) -> None:
    return await pm.hook.dispose_gen_image()


async def generate_image(pm: PluginManager, prompt: str) -> bytes | None:
    return await pm.hook.generate_image(prompt=prompt)