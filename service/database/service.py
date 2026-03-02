from model.episode import Episode
from model.program import Program
from model.station import RadioStation
from service.database.interface import AbstractDatabaseBackend


class DatabaseService:
    """事件驱动逻辑直接依赖的数据库服务层"""

    def __init__(self, backend: AbstractDatabaseBackend) -> None:
        self._backend = backend

    async def initialize(self) -> None:
        await self._backend.initialize()

    async def write_episode(self, episode: Episode) -> None:
        await self._backend.write_episode(episode)

    async def write_program(self, program: Program) -> None:
        await self._backend.write_program(program)

    async def write_station(self, station: RadioStation) -> None:
        await self._backend.write_station(station)

    async def query_episode(self, uuid: bytes) -> Episode | None:
        return await self._backend.query_episode(uuid)

    async def query_program(self, uuid: bytes) -> Program | None:
        return await self._backend.query_program(uuid)

    async def query_station(self, uuid: bytes) -> RadioStation | None:
        return await self._backend.query_station(uuid)

    async def delete_episode(self, uuid: bytes) -> bool:
        return await self._backend.delete_episode(uuid)

    async def delete_program(self, uuid: bytes) -> bool:
        return await self._backend.delete_program(uuid)

    async def delete_station(self, uuid: bytes) -> bool:
        return await self._backend.delete_station(uuid)
