import asyncio
import logging

from aioquic.asyncio.server import serve
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration
from pyfiglet import figlet_format
from rich.logging import RichHandler

from handler.broadcast import BroadcastHandler
from service.connection.app import WebTransportApp
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


async def main():
    app = WebTransportApp()
    app.add_route("/broadcast", BroadcastHandler)

    # 全局广播服务
    config = CaptureConfig(
        device=1,
        blocksize=CaptureBlockSize.B8192,
        channel=CaptureChannel.Stereo,
        dtype=CaptureDtype.Bit24,
        samplerate=CaptureSampleRate.R48000,
    )
    fetch_service = FetchService(config=config)
    asyncio.create_task(fetch_service.start())

    # 加载 TLS 证书
    configuration = QuicConfiguration(
        alpn_protocols=H3_ALPN, is_client=False, max_datagram_frame_size=65536
    )
    configuration.load_cert_chain(
        "cert/wthomec4.dns.army.cer",
        "cert/wthomec4.dns.army.key",
    )

    # 启动 QUIC 服务器
    log.info("正在注册 wthomec4.dns.army:8908 以作为服务")
    server = await serve(
        host="wthomec4.dns.army",
        port=8908,
        configuration=configuration,
        create_protocol=lambda *args, **kwargs: WebTransportProtocol(
            *args, app=app, **kwargs
        ),
    )
    log.info("启动 QUIC HTTP/3 服务器，监听 0.0.0.0:8908")
    log.info("WebTransport 广播端点: https://wthomec4.dns.army:8908/broadcast")

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
