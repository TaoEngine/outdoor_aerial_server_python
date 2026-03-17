import logging

from pluggy import PluginManager


log = logging.getLogger(__name__)


async def process_episode(pm: PluginManager) -> None:
    # response = await plugin_call(pm, "request_multimodal", model="123", prompt="你好")
    # log.info(response[0])
    ...