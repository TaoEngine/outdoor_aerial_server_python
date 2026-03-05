from pluggy import HookspecMarker

from model import Episode
from model import Program
from model import Station

hookspec = HookspecMarker("outdoor.aerial.sever")


class DatabaseSpec:
    """为插件开发暴露的数据库接口模板"""

    @hookspec
    async def init_database(self) -> None:
        """新建数据库文件或格式化数据库，并初始化数据库结构"""
        ...

    @hookspec
    async def dispose_database(self) -> None:
        """解除数据库"""
        ...

    @hookspec
    async def write_episode(self, episode: Episode) -> None:
        """写入或覆盖单期节目"""
        ...

    @hookspec
    async def write_program(self, program: Program) -> None:
        """写入或覆盖电台节目"""
        ...

    @hookspec
    async def write_station(self, station: Station) -> None:
        """写入或覆盖广播电台"""
        ...

    @hookspec
    async def query_episode(self, uuid: bytes) -> Episode | None:
        """按 uuid 查询单期节目"""
        ...

    @hookspec
    async def query_program(self, uuid: bytes) -> Program | None:
        """按 uuid 查询电台节目"""
        ...

    @hookspec
    async def query_station(self, uuid: bytes) -> Station | None:
        """按 uuid 查询广播电台"""
        ...

    @hookspec
    async def delete_episode(self, uuid: bytes) -> bool:
        """删除单期节目"""
        ...

    @hookspec
    async def delete_program(self, uuid: bytes) -> bool:
        """删除电台节目"""
        ...

    @hookspec
    async def delete_station(self, uuid: bytes) -> bool:
        """删除广播电台"""
        ...
