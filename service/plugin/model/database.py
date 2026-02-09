from abc import ABC, abstractmethod

from service.plugin.interface.dataclass import PluginInfo


class DatabasePlugin(ABC):
    """数据库插件模板"""

    plugin_info: PluginInfo
    """数据库插件的信息"""

    @abstractmethod
    async def setup(self, context) -> None:
        """
        数据库插件初始化过程

        可以在这里进行初始化数据库与连接数据库等操作
        """
