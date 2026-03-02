import asyncio
import json
import sqlite3
from datetime import datetime, time
from pathlib import Path

from yarl import URL

from model.episode import Episode
from model.program import Program, ProgramStatus, ProgramType, ProgramWeekday
from model.station import RadioStation, StationStatus, StationType
from service.database.interface import AbstractDatabaseBackend
from service.plugin.interface.dataclass import PluginInfo
from service.plugin.model.database import DatabasePlugin


class SQLiteDatabaseBackend(AbstractDatabaseBackend):
    """SQLite 数据库后端"""

    def __init__(self, path: str = "asset/db/radio.db") -> None:
        database_path = Path(path)
        database_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        await self._run(self._initialize_sync)

    async def write_episode(self, episode: Episode) -> None:
        await self._run(self._save_episode_sync, episode)

    async def write_program(self, program: Program) -> None:
        await self._run(self._save_program_sync, program)

    async def write_station(self, station: RadioStation) -> None:
        await self._run(self._save_station_sync, station)

    async def query_episode(self, uuid: bytes) -> Episode | None:
        return await self._run(self._query_episode_sync, uuid)

    async def query_program(self, uuid: bytes) -> Program | None:
        return await self._run(self._query_program_sync, uuid)

    async def query_station(self, uuid: bytes) -> RadioStation | None:
        return await self._run(self._query_station_sync, uuid)

    async def delete_episode(self, uuid: bytes) -> bool:
        return await self._run(self._delete_episode_sync, uuid)

    async def delete_program(self, uuid: bytes) -> bool:
        return await self._run(self._delete_program_sync, uuid)

    async def delete_station(self, uuid: bytes) -> bool:
        return await self._run(self._delete_station_sync, uuid)

    async def _run(self, fn, *args):
        async with self._lock:
            return await asyncio.to_thread(fn, *args)

    def _initialize_sync(self) -> None:
        self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS station (
                uuid BLOB PRIMARY KEY,
                logo BLOB NOT NULL,
                banner BLOB NOT NULL,
                frequency REAL NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                station_type INTEGER NOT NULL,
                station_status INTEGER NOT NULL,
                institution TEXT NOT NULL,
                language_primary TEXT NOT NULL,
                language_region TEXT NOT NULL,
                social TEXT,
                like_flag INTEGER NOT NULL CHECK (like_flag IN (0, 1)),
                block_flag INTEGER NOT NULL CHECK (block_flag IN (0, 1)),
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS program (
                uuid BLOB PRIMARY KEY,
                studio BLOB NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                program_type INTEGER NOT NULL,
                program_status INTEGER NOT NULL,
                hosts TEXT,
                like_flag INTEGER NOT NULL CHECK (like_flag IN (0, 1)),
                block_flag INTEGER NOT NULL CHECK (block_flag IN (0, 1)),
                date_list TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS episode (
                uuid BLOB PRIMARY KEY,
                program BLOB NOT NULL,
                cover BLOB NOT NULL,
                title TEXT NOT NULL,
                abstract TEXT NOT NULL,
                favorite_flag INTEGER NOT NULL CHECK (favorite_flag IN (0, 1)),
                publish_time TEXT NOT NULL
            );
        """)
        self._connection.commit()

    def _save_episode_sync(self, episode: Episode) -> None:
        self._connection.execute(
            """
            INSERT INTO episode (uuid, program, cover, title, abstract, favorite_flag, publish_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                program = excluded.program,
                cover = excluded.cover,
                title = excluded.title,
                abstract = excluded.abstract,
                favorite_flag = excluded.favorite_flag,
                publish_time = excluded.publish_time
            """,
            (
                episode.uuid,
                episode.program,
                episode.cover,
                episode.title,
                episode.abstract,
                int(episode.favorite),
                episode.time.isoformat(),
            ),
        )
        self._connection.commit()

    def _save_program_sync(self, program: Program) -> None:
        self._connection.execute(
            """
            INSERT INTO program (
                uuid, studio, name, description, program_type, program_status,
                hosts, like_flag, block_flag, date_list, start_time, end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                studio = excluded.studio,
                name = excluded.name,
                description = excluded.description,
                program_type = excluded.program_type,
                program_status = excluded.program_status,
                hosts = excluded.hosts,
                like_flag = excluded.like_flag,
                block_flag = excluded.block_flag,
                date_list = excluded.date_list,
                start_time = excluded.start_time,
                end_time = excluded.end_time
            """,
            (
                program.uuid,
                program.studio,
                program.name,
                program.description,
                program.type.value,
                program.status.value,
                json.dumps(program.hosts) if program.hosts is not None else None,
                int(program.like),
                int(program.block),
                json.dumps([weekday.value for weekday in program.date]),
                program.start.isoformat(),
                program.end.isoformat(),
            ),
        )
        self._connection.commit()

    def _save_station_sync(self, station: RadioStation) -> None:
        self._connection.execute(
            """
            INSERT INTO station (
                uuid, logo, banner, frequency, name, description, station_type,
                station_status, institution, language_primary, language_region,
                social, like_flag, block_flag, start_time, end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                logo = excluded.logo,
                banner = excluded.banner,
                frequency = excluded.frequency,
                name = excluded.name,
                description = excluded.description,
                station_type = excluded.station_type,
                station_status = excluded.station_status,
                institution = excluded.institution,
                language_primary = excluded.language_primary,
                language_region = excluded.language_region,
                social = excluded.social,
                like_flag = excluded.like_flag,
                block_flag = excluded.block_flag,
                start_time = excluded.start_time,
                end_time = excluded.end_time
            """,
            (
                station.uuid,
                station.logo,
                station.banner,
                station.frequency,
                station.name,
                station.description,
                station.type.value,
                station.status.value,
                station.institution,
                station.language[0],
                station.language[1],
                str(station.social) if station.social is not None else None,
                int(station.like),
                int(station.block),
                station.start.isoformat(),
                station.end.isoformat(),
            ),
        )
        self._connection.commit()

    def _query_episode_sync(self, uuid: bytes) -> Episode | None:
        row = self._connection.execute(
            """
            SELECT uuid, program, cover, title, abstract, favorite_flag, publish_time
            FROM episode
            WHERE uuid = ?
            """,
            (uuid,),
        ).fetchone()
        if row is None:
            return None
        return Episode(
            program=row["program"],
            uuid=row["uuid"],
            cover=row["cover"],
            title=row["title"],
            abstract=row["abstract"],
            favorite=bool(row["favorite_flag"]),
            time=datetime.fromisoformat(row["publish_time"]),
        )

    def _query_program_sync(self, uuid: bytes) -> Program | None:
        row = self._connection.execute(
            """
            SELECT
                uuid, studio, name, description, program_type, program_status,
                hosts, like_flag, block_flag, date_list, start_time, end_time
            FROM program
            WHERE uuid = ?
            """,
            (uuid,),
        ).fetchone()
        if row is None:
            return None
        hosts = json.loads(row["hosts"]) if row["hosts"] is not None else None
        date_list: list[int] = json.loads(row["date_list"])
        return Program(
            studio=row["studio"],
            uuid=row["uuid"],
            name=row["name"],
            description=row["description"],
            type=ProgramType(row["program_type"]),
            status=ProgramStatus(row["program_status"]),
            hosts=hosts,
            like=bool(row["like_flag"]),
            block=bool(row["block_flag"]),
            date=[ProgramWeekday(day) for day in date_list],
            start=time.fromisoformat(row["start_time"]),
            end=time.fromisoformat(row["end_time"]),
        )

    def _query_station_sync(self, uuid: bytes) -> RadioStation | None:
        row = self._connection.execute(
            """
            SELECT
                uuid, logo, banner, frequency, name, description, station_type,
                station_status, institution, language_primary, language_region,
                social, like_flag, block_flag, start_time, end_time
            FROM station
            WHERE uuid = ?
            """,
            (uuid,),
        ).fetchone()
        if row is None:
            return None
        social = URL(row["social"]) if row["social"] is not None else None
        return RadioStation(
            uuid=row["uuid"],
            logo=row["logo"],
            banner=row["banner"],
            frequency=row["frequency"],
            name=row["name"],
            description=row["description"],
            type=StationType(row["station_type"]),
            status=StationStatus(row["station_status"]),
            institution=row["institution"],
            language=(row["language_primary"], row["language_region"]),
            social=social,
            like=bool(row["like_flag"]),
            block=bool(row["block_flag"]),
            start=time.fromisoformat(row["start_time"]),
            end=time.fromisoformat(row["end_time"]),
        )

    def _delete_episode_sync(self, uuid: bytes) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM episode WHERE uuid = ?",
            (uuid,),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def _delete_program_sync(self, uuid: bytes) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM program WHERE uuid = ?",
            (uuid,),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def _delete_station_sync(self, uuid: bytes) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM station WHERE uuid = ?",
            (uuid,),
        )
        self._connection.commit()
        return cursor.rowcount > 0


class SQLitePlugin(DatabasePlugin):
    plugin_info = PluginInfo(
        name="sqlite",
        description="使用 SQLite 作为服务端数据库后端",
        author="TaoEngine",
        license="MIT",
        version="0.1.0",
    )

    def create_backend(self, **kwargs) -> AbstractDatabaseBackend:
        path = kwargs.get("path", "asset/db/radio.db")
        return SQLiteDatabaseBackend(path=path)

    async def setup(self, context: AbstractDatabaseBackend) -> None:
        await context.initialize()


def create_plugin() -> SQLitePlugin:
    return SQLitePlugin()
