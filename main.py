import asyncio
import logging
from pluggy import PluginManager
from pyfiglet import figlet_format
from rich.logging import RichHandler

from plugin.manager import build_plugin_manager
from service import init_plugin, process_plugin, dispose_plugin

logging.basicConfig(
    level="INFO",
    format="%(name)s: %(message)s",
    handlers=[
        RichHandler(
            log_time_format="[%H:%M:%S]",
            rich_tracebacks=True,
        )
    ],
)
log = logging.getLogger(__name__)
pm: PluginManager = build_plugin_manager()


async def main():
    await init_plugin(pm)
    await process_plugin(pm)
    await dispose_plugin(pm)


if __name__ == "__main__":
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")
    asyncio.run(main())
