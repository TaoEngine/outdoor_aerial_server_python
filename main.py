import asyncio
import logging

from aioquic.asyncio.server import serve
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration
from pyfiglet import figlet_format
from rich.logging import RichHandler

from handler.broadcast import BroadcastHandler
from service.connection.router import WebTransportRouter
from service.connection.protocol import WebTransportProtocol
from service.controller import CaptureConfig, FetchService
from service.controller.dataclass import (
    CaptureBlockSize,
    CaptureChannel,
    CaptureDtype,
    CaptureSampleRate,
)

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
    # 广播信号采集服务
    fetch_service = FetchService(config=config)
    asyncio.create_task(fetch_service.start())

    # HTTP/3 WebTransport 服务
    log.info("正在注册 https://wthomec4.dns.army:8908 以作为服务")
    app = WebTransportRouter()
    app.add_route("/broadcast", BroadcastHandler)
    server = await serve(
        host="wthomec4.dns.army",
        port=8908,
        configuration=configuration,
        create_protocol=lambda *args, **kwargs: WebTransportProtocol(
            *args, app=app, **kwargs
        ),
    )

    try:
        await asyncio.Future()  # 永久运行
    except KeyboardInterrupt:
        log.info("服务器正在关闭...")
    finally:
        fetch_service.stop()
        server.close()


if __name__ == "__main__":
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")
    asyncio.run(main())
