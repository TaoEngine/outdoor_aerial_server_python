import logging

from pluggy import PluginManager

from plugin import call_plugin

log = logging.getLogger(__name__)


async def process_episode(pm: PluginManager) -> None:
    response = await call_plugin(pm, "request_multimodal", model="123", prompt="你好")
    log.info(response[0])
