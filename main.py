import asyncio
import logging
from typing import Optional

from aioquic.asyncio.server import QuicServer
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration
from pyfiglet import figlet_format
from rich.logging import RichHandler

from service.connection import start_webtransport_service
from service.controller import CaptureConfig, start_fetch_service
from service.controller.interface.dataclass import (
    CaptureBlockSize,
    CaptureChannel,
    CaptureDtype,
    CaptureSampleRate,
)
from service.controller.fetch import FetchService

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

config = CaptureConfig(
    device=1,
    blocksize=CaptureBlockSize.B8192,
    channel=CaptureChannel.Stereo,
    dtype=CaptureDtype.Bit24,
    samplerate=CaptureSampleRate.R48000,
)

configuration = QuicConfiguration(
    alpn_protocols=H3_ALPN,
    is_client=False,
)
configuration.load_cert_chain(
    "cert/wthomec4.dns.army.cer",
    "cert/wthomec4.dns.army.key",
)


async def main():
    fetch_service: Optional[FetchService] = None
    webtransport_service: Optional[QuicServer] = None
    try:
        # 广播信号采集分发服务
        fetch_service = await start_fetch_service(config=config)

        # HTTP/3 WebTransport 服务
        webtransport_service = await start_webtransport_service(
            configuration=configuration,
            host="wthomec4.dns.army",
        )

        # 服务持续运行
        await asyncio.Future()
    finally:
        if fetch_service:
            fetch_service.stop()
        if webtransport_service:
            webtransport_service.close()


if __name__ == "__main__":
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("服务被 Ctrl+C 终止运行")
