from dataclasses import dataclass


@dataclass(frozen=True)
class PluginInfo:
    """插件的信息"""

    name: str
    """插件的名称"""

    description: str
    """插件的用途"""

    author: str
    """插件的作者"""

    license: str
    """插件的许可"""

    version: str
    """插件的版本"""
