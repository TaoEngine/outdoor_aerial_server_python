"""基于 WebTransport 参与客户端通信的模块"""

import logging
from socket import gaierror
from typing import Optional

from aioquic.asyncio.server import serve, QuicServer
from aioquic.quic.configuration import QuicConfiguration

from handler.broadcast import BroadcastHandler
from service.connection.protocol import WebTransportProtocol
from service.connection.router import WebTransportRouter

log = logging.getLogger(__name__)


async def start_webtransport_service(
    configuration: QuicConfiguration,
    host: str,
    port: int = 58908,
) -> Optional[QuicServer]:
    """启动 HTTP/3 WebTransport 服务"""
    app = WebTransportRouter()
    app.add_route("/broadcast", BroadcastHandler)

    try:
        server = await serve(
            host=host,
            port=port,
            configuration=configuration,
            create_protocol=lambda *args, **kwargs: WebTransportProtocol(
                app=app,
                *args,
                **kwargs,
            ),
        )
        log.info(f"已绑定 {host} 域名作为服务入口 端口为 {port}")
        return server
    except gaierror:
        # 域名不存在
        log.fatal(f"{host} 是个并不存在的域名")
    except OSError:
        # 域名无法绑定
        log.fatal(f"{host} 域名未与本机的 IP 绑定在一起")
