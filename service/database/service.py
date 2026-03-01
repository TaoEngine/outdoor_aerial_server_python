from model.episode import Episode
from model.program import Program
from model.station import RadioStation
from service.database.interface import DatabaseBackend


class DatabaseService:
    """事件驱动逻辑直接依赖的数据库服务层"""

    def __init__(self, backend: DatabaseBackend) -> None:
        self._backend = backend

    async def initialize(self) -> None:
        await self._backend.initialize()

    async def save_episode(self, episode: Episode) -> None:
        await self._backend.save_episode(episode)

    async def save_program(self, program: Program) -> None:
        await self._backend.save_program(program)

    async def save_station(self, station: RadioStation) -> None:
        await self._backend.save_station(station)

    async def get_episode(self, uuid: bytes) -> Episode | None:
        return await self._backend.get_episode(uuid)

    async def get_program(self, uuid: bytes) -> Program | None:
        return await self._backend.get_program(uuid)

    async def get_station(self, uuid: bytes) -> RadioStation | None:
        return await self._backend.get_station(uuid)

    async def delete_episode(self, uuid: bytes) -> bool:
        return await self._backend.delete_episode(uuid)

    async def delete_program(self, uuid: bytes) -> bool:
        return await self._backend.delete_program(uuid)

    async def delete_station(self, uuid: bytes) -> bool:
        return await self._backend.delete_station(uuid)
