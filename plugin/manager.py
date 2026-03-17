from pluggy import PluginManager

from .spec import (
    MultiModelSpec,
    ConnectionSpec,
    DatabaseSpec,
    RepositorySpec,
    TunerSpec,
)

PROJECT_NAME = "outdoor.aerial.sever"
ENTRYPOINT_GROUP = "outdoor.aerial.plugins"


def build_plugin_manager(load_entrypoints: bool = True) -> PluginManager:
    """建立插件绑定"""

    pm = PluginManager(PROJECT_NAME)
    pm.add_hookspecs(MultiModelSpec)
    pm.add_hookspecs(ConnectionSpec)
    pm.add_hookspecs(DatabaseSpec)
    pm.add_hookspecs(RepositorySpec)
    pm.add_hookspecs(TunerSpec)
    if load_entrypoints:
        pm.load_setuptools_entrypoints(ENTRYPOINT_GROUP)
    return pm
