from abc import ABC, abstractmethod

from service.plugin.interface.dataclass import PluginInfo


class RobotPlugin(ABC):
    """智能体插件模板"""

    plugin_info: PluginInfo
    """智能体插件的信息"""

    @abstractmethod
    async def setup(self, context) -> None:
        """智能体插件初始化过程"""
