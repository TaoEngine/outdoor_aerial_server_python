from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from service.plugin.interface.dataclass import PluginInfo

if TYPE_CHECKING:
    from service.database.interface import AbstractDatabaseBackend


class DatabasePlugin(ABC):
    """数据库插件模板"""

    plugin_info: PluginInfo
    """数据库插件的信息"""

    @abstractmethod
    def create_backend(self, **kwargs) -> "AbstractDatabaseBackend":
        """创建数据库后端实例"""

    @abstractmethod
    async def setup(self, context: "AbstractDatabaseBackend") -> None:
        """
        数据库插件初始化过程

        可以在这里进行初始化数据库与连接数据库等操作
        """
