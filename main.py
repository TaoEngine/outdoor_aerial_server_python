import trio
import logging
from pyfiglet import figlet_format
from rich.logging import RichHandler

from service import runtime

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


if __name__ == "__main__":
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")
    trio.run(runtime)
