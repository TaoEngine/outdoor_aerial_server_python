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
        for folder in Path("plugin").iterdir():
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
                moudle: ModuleType = module_from_spec(spec)
                if spec.loader:
                    spec.loader.exec_module(moudle)
                plugin: PluginModel = moudle.create_plugin()
                self.__plugins[plugin.plugin_info.name] = plugin
