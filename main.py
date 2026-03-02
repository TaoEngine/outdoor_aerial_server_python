import asyncio
import logging
from aioquic.h3.connection import H3_ALPN
from aioquic.quic.configuration import QuicConfiguration
from pyfiglet import figlet_format
from rich.logging import RichHandler

from handler.broadcast import BroadcastHandler
from event import (
    ConnectionOptions,
    ConnectionRoute,
    EventBus,
    register_connection_service,
    register_controller_service,
    register_database_service,
)
from service.controller import CaptureConfig
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
    "asset/cert/wthomec4.dns.army.cer",
    "asset/cert/wthomec4.dns.army.key",
)


async def main():
    bus = EventBus()

    # 注册广播信号采集分发服务
    register_controller_service(bus, config=config)

    # 注册数据库服务（默认使用 sqlite 插件）
    register_database_service(bus)

    # 注册 HTTP/3 WebTransport 连接服务
    register_connection_service(
        bus,
        ConnectionOptions(
            configuration=configuration,
            host="wthomec4.dns.army",
            routes=[
                ConnectionRoute(
                    "/broadcast",
                    BroadcastHandler,
                    kwargs_factory=lambda services: {
                        "fetch_service": services.controller,
                    },
                ),
            ],
        ),
    )

    try:
        await bus.startup_services()
        # 服务持续运行
        await asyncio.Future()
    finally:
        await bus.shutdown_services()


if __name__ == "__main__":
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("服务被 Ctrl+C 终止运行")
