"""WebTransport 连接中使用的数据结构说明。"""

from dataclasses import dataclass
from typing import Any, Optional

from yarl import URL

from doc.connection.handler import HandlerFactory
from doc.connection.interface.enum import H3Method, H3Protocol, H3Scheme


@dataclass(frozen=True)
class HeaderInfo:
    """HTTP/3 请求方发起的请求信息。"""

    authority: URL
    """HTTP/3 请求方请求的地址。"""

    origin: Optional[URL]
    """HTTP/3 的请求方地址。"""

    path: URL
    """HTTP/3 的连接端点。"""

    scheme: H3Scheme
    """HTTP/3 的连接方案。"""

    method: Optional[H3Method]
    """HTTP/3 的连接请求方法。"""

    protocol: Optional[H3Protocol]
    """HTTP/3 的连接协议。"""

    @classmethod
    def from_header(cls, header: list[tuple[bytes, bytes]]) -> "HeaderInfo":
        """从 aioquic 的 header 中解析出请求信息。"""


@dataclass(frozen=True)
class RouteInfo:
    """WebTransport 的路由信息。"""

    handler_factory: HandlerFactory
    """用于创建处理器实例的工厂。"""

    kwargs: dict[str, Any]
    """创建处理器时附带的路由参数。"""


@dataclass(frozen=True)
class SessionInfo:
    """WebTransport 单次连接事件中的基础信息。"""

    stream_id: int
    """请求方申请的连接 ID。"""

    path: URL
    """请求方访问的端点（包含查询参数）。"""

    client: Optional[tuple[str, int] | str]
    """此次连接事件的客户端信息。"""
