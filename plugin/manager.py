import inspect
from typing import Awaitable, Callable, Iterable, cast

from pluggy import PluginManager

from .spec import ConnectionSpec, DatabaseSpec, RepositorySpec, TunerSpec

PROJECT_NAME = "outdoor.aerial.sever"
ENTRYPOINT_GROUP = "outdoor.aerial.plugins"


def build_plugin_manager(load_entrypoints: bool = True) -> PluginManager:
    pm = PluginManager(PROJECT_NAME)
    pm.add_hookspecs(ConnectionSpec)
    pm.add_hookspecs(DatabaseSpec)
    pm.add_hookspecs(RepositorySpec)
    pm.add_hookspecs(TunerSpec)
    if load_entrypoints:
        pm.load_setuptools_entrypoints(ENTRYPOINT_GROUP)
    return pm


async def hook_plugin(
    pm: PluginManager,
    hook_name: str,
    *args: object,
    **kwargs: object,
) -> list[object]:
    hook = cast(
        Callable[..., Iterable[object | Awaitable[object]]],
        getattr(pm.hook, hook_name),
    )
    results = hook(*args, **kwargs)
    callback: list[object] = []

    for result in results:
        if inspect.isawaitable(result):
            callback.append(await cast(Awaitable[object], result))
        else:
            callback.append(result)

    return callback
