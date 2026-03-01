from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import Union

from service.plugin.model.database import DatabasePlugin
from service.plugin.model.robot import RobotPlugin

PluginModel = Union[DatabasePlugin, RobotPlugin]


class PluginRegistry:
    def __init__(self) -> None:
        self.__plugins: dict[str, PluginModel] = dict()

    def load(self) -> None:
        for folder in Path("asset/plugin").iterdir():
            # 不处理根目录文件
            if not folder.is_dir():
                continue
            # 只导入有 plugin.py 的文件夹
            module_path = folder / "plugin.py"
            if not module_path.exists():
                continue

            # 分配导入插件
            spec = spec_from_file_location(folder.name, module_path)
            if spec:
                module: ModuleType = module_from_spec(spec)
                if spec.loader:
                    spec.loader.exec_module(module)
                plugin: PluginModel = module.create_plugin()
                self.__plugins[plugin.plugin_info.name] = plugin

    def get(self, name: str) -> PluginModel | None:
        """按名称读取已注册插件"""
        return self.__plugins.get(name)

    def get_database_plugin(self, name: str) -> DatabasePlugin | None:
        """按名称读取数据库插件"""
        plugin = self.get(name)
        if isinstance(plugin, DatabasePlugin):
            return plugin
        return None
