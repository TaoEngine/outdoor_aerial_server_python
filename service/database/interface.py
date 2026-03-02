from abc import ABC, abstractmethod

from model.episode import Episode
from model.program import Program
from model.station import RadioStation


class AbstractDatabaseBackend(ABC):
    """为插件开发暴露的数据库后端接口模板"""

    @abstractmethod
    async def initialize(self) -> None:
        """新建数据库文件或格式化数据库，并初始化数据库结构"""

    @abstractmethod
    async def write_episode(self, episode: Episode) -> None:
        """写入或覆盖单期节目"""

    @abstractmethod
    async def write_program(self, program: Program) -> None:
        """写入或覆盖电台节目"""

    @abstractmethod
    async def write_station(self, station: RadioStation) -> None:
        """写入或覆盖广播电台"""

    @abstractmethod
    async def query_episode(self, uuid: bytes) -> Episode | None:
        """按 uuid 查询单期节目"""

    @abstractmethod
    async def query_program(self, uuid: bytes) -> Program | None:
        """按 uuid 查询电台节目"""

    @abstractmethod
    async def query_station(self, uuid: bytes) -> RadioStation | None:
        """按 uuid 查询广播电台"""

    @abstractmethod
    async def delete_episode(self, uuid: bytes) -> bool:
        """删除单期节目"""

    @abstractmethod
    async def delete_program(self, uuid: bytes) -> bool:
        """删除电台节目"""

    @abstractmethod
    async def delete_station(self, uuid: bytes) -> bool:
        """删除广播电台"""
