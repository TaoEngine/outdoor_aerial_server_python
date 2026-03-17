from pluggy import PluginManager

from model import Episode, Program, Station


async def init_database(pm: PluginManager) -> None:
    return await pm.hook.init_database()


async def dispose_database(pm: PluginManager) -> None:
    return await pm.hook.dispose_database()


async def write_episode(pm: PluginManager, episode: Episode) -> None:
    return await pm.hook.write_episode(episode=episode)


async def write_program(pm: PluginManager, program: Program) -> None:
    return await pm.hook.write_program(program=program)


async def write_station(pm: PluginManager, station: Station) -> None:
    return await pm.hook.write_station(station=station)


async def query_episode(pm: PluginManager, uuid: bytes) -> Episode | None:
    return await pm.hook.query_episode(uuid=uuid)


async def query_program(pm: PluginManager, uuid: bytes) -> Program | None:
    return await pm.hook.query_program(uuid=uuid)


async def query_station(pm: PluginManager, uuid: bytes) -> Station | None:
    return await pm.hook.query_station(uuid=uuid)


async def delete_episode(pm: PluginManager, uuid: bytes) -> bool:
    return await pm.hook.delete_episode(uuid=uuid)


async def delete_program(pm: PluginManager, uuid: bytes) -> bool:
    return await pm.hook.delete_program(uuid=uuid)


async def delete_station(pm: PluginManager, uuid: bytes) -> bool:
    return await pm.hook.delete_station(uuid=uuid)