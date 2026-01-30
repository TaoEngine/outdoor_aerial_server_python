import asyncio
import logging
from typing import Optional

from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.asyncio.server import serve
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import (
    DataReceived,
    H3Event,
    HeadersReceived,
    WebTransportStreamDataReceived,
)
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from pyfiglet import figlet_format
from rich.logging import RichHandler

from handler.broadcast import BroadcastHandler
from service.capture import CaptureService, BroadcastConfig
from service.capture.dataclass import BroadcastBlockSize

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

# 全局广播服务
config = BroadcastConfig(device=0)
broadcast_service = CaptureService(config=config)


class WebTransportProtocol(QuicConnectionProtocol):
    """WebTransport over HTTP/3 协议处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._h3: Optional[H3Connection] = None
        self._broadcast_handler: Optional[BroadcastHandler] = None

    def quic_event_received(self, event: QuicEvent) -> None:
        """处理 QUIC 事件"""
        if isinstance(event, StreamDataReceived):
            # 初始化 H3 连接
            if self._h3 is None:
                self._h3 = H3Connection(self._quic, enable_webtransport=True)
                self._broadcast_handler = BroadcastHandler(
                    self._h3, broadcast_service
                )

            # 处理 HTTP/3 事件
            for h3_event in self._h3.handle_event(event):
                self._handle_h3_event(h3_event)

    def _handle_h3_event(self, event: H3Event) -> None:
        """处理 HTTP/3 事件"""
        if isinstance(event, HeadersReceived):
            self._handle_headers(event)
        elif isinstance(event, WebTransportStreamDataReceived):
            # 转发给 broadcast handler
            if self._broadcast_handler:
                self._broadcast_handler.handle_event(event)
        elif isinstance(event, DataReceived):
            # 标准 HTTP 数据，检查是否为 WebTransport 会话的一部分
            pass

    def _handle_headers(self, event: HeadersReceived) -> None:
        """处理 HTTP 请求头"""
        headers = dict((k.decode(), v.decode()) for k, v in event.headers)
        method = headers.get(":method", "")
        path = headers.get(":path", "")
        protocol = headers.get(":protocol", "")

        log.info(f"{method} {path} ({protocol})")

        # WebTransport CONNECT 请求
        if method == "CONNECT" and protocol == "webtransport":
            if path == "/broadcast":
                self._accept_webtransport(event.stream_id)
            else:
                self._reject_request(event.stream_id, 404)
        else:
            # 普通 HTTP 请求
            self._send_http_response(event.stream_id)

    def _accept_webtransport(self, stream_id: int) -> None:
        """接受 WebTransport 连接"""
        assert self._h3 is not None
        self._h3.send_headers(
            stream_id=stream_id,
            headers=[
                (b":status", b"200"),
                (b"sec-webtransport-http3-draft", b"draft02"),
            ],
        )
        # 通知 broadcast handler 新连接
        if self._broadcast_handler:
            self._broadcast_handler.handle_event(
                HeadersReceived(
                    headers=[(b":method", b"CONNECT"), (b":path", b"/broadcast")],
                    stream_id=stream_id,
                    stream_ended=False,
                )
            )
        log.info(f"WebTransport 会话 {stream_id} 已建立 (路径: /broadcast)")

    def _reject_request(self, stream_id: int, status: int) -> None:
        """拒绝请求"""
        assert self._h3 is not None
        self._h3.send_headers(
            stream_id=stream_id,
            headers=[(b":status", str(status).encode())],
        )

    def _send_http_response(self, stream_id: int) -> None:
        """发送普通 HTTP 响应"""
        assert self._h3 is not None
        self._h3.send_headers(
            stream_id=stream_id,
            headers=[
                (b":status", b"200"),
                (b"content-type", b"text/plain"),
            ],
        )
        self._h3.send_data(
            stream_id=stream_id,
            data=b"Outdoor Aerial QUIC Server",
            end_stream=True,
        )


async def main():
    """主入口"""
    log.info(f"\n{figlet_format('Outdoor Aerial')}\n永远热爱户外和广播！")

    # 加载 TLS 证书
    cert_path = "cert/localhost.crt"
    key_path = "cert/localhost.key"

    configuration = QuicConfiguration(
        alpn_protocols=["h3"],
        is_client=False,
        max_datagram_frame_size=65536,
    )

    # 加载 TLS 证书
    try:
        configuration.load_cert_chain(cert_path, key_path)
    except Exception:
        log.error(f"TLS 证书不存在，请提供 {cert_path} 和 {key_path}")
        log.info("可以使用 openssl 生成自签名证书:")
        log.info('  openssl req -x509 -nodes -days 365 -newkey rsa:2048 '
                '-keyout key.pem -out cert.pem -subj "/CN=localhost"')
    

    log.info("启动 QUIC HTTP/3 服务器，监听 0.0.0.0:8908")
    log.info("WebTransport 广播端点: https://localhost:8908/broadcast")

    # 启动广播服务
    asyncio.create_task(broadcast_service.stream())

    # 启动 QUIC 服务器
    server = await serve(
        host="0.0.0.0",
        port=8908,
        configuration=configuration,
        create_protocol=WebTransportProtocol,
    )

    try:
        await asyncio.Future()  # 永久运行
    except KeyboardInterrupt:
        log.info("服务器正在关闭...")
    finally:
        broadcast_service.stop()
        server.close()


if __name__ == "__main__":
    asyncio.run(main())
