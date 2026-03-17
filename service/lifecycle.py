import logging

from asyncio import TaskGroup, Event
from pluggy import PluginManager

from plugin.interface import (
    init_connection,
    init_database,
    init_gen_image,
    init_multimodel,
    init_repository,
    init_tuner,
    dispose_connection,
    dispose_database,
    dispose_gen_image,
    dispose_multimodel,
    dispose_repository,
    dispose_tuner,
)

from .run_broadcast import run_broadcast
from .process_episode import process_episode

log = logging.getLogger(__name__)


async def init_plugin(pm: PluginManager) -> None:
    try:
        async with TaskGroup() as group:
            group.create_task(init_connection(pm))
            group.create_task(init_database(pm))
            group.create_task(init_gen_image(pm))
            group.create_task(init_multimodel(pm))
            group.create_task(init_repository(pm))
            group.create_task(init_tuner(pm))
        log.info("已初始化所有服务")
    except ExceptionGroup as e:
        log.critical("初始化相关服务时出现错误")
    finally:
        ...


async def process_plugin(pm: PluginManager):
    try:
        event = Event()
        async with TaskGroup() as group:
            group.create_task(run_broadcast(pm, event))
            group.create_task(process_episode(pm))
    except ExceptionGroup:
        log.critical("处理相关服务时出现错误")
    except KeyboardInterrupt:
        log.critical("服务被 Ctrl+C 终止运行")


async def dispose_plugin(pm: PluginManager) -> None:
    try:
        async with TaskGroup() as group:
            group.create_task(dispose_connection(pm))
            group.create_task(dispose_database(pm))
            group.create_task(dispose_gen_image(pm))
            group.create_task(dispose_multimodel(pm))
            group.create_task(dispose_repository(pm))
            group.create_task(dispose_tuner(pm))
        log.info("已解除所有服务")
    except ExceptionGroup as e:
        log.critical("解除相关服务时出现错误")
    finally:
        ...
