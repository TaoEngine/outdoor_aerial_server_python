from pluggy import HookspecMarker
from typing import BinaryIO

hookspec = HookspecMarker("outdoor.aerial.sever")


class RepositorySpec:
    """为插件开发暴露的存储接口模板"""

    @hookspec
    async def init_repository(self) -> None:
        """初始化存储接口"""
        ...

    @hookspec
    async def dispose_repository(self) -> None:
        """解除存储接口"""
        ...

    @hookspec
    async def save_episode(self, uuid: bytes, data: BinaryIO) -> None:
        """实时存储节目"""
        ...

    @hookspec
    def read_episode(self)-> tuple[bytes, BinaryIO]:
        """读取节目"""
        ...