from dataclasses import dataclass
from typing import Any

from yarl import URL

from service.connection.interface import HandlerFactory


@dataclass(frozen=True)
class HeaderInfo:
    """HTTP/3 请求方发起的请求信息"""

    target: URL
    """HTTP/3 的请求头"""

    method: str | None
    """HTTP/3 的连接请求"""

    protocol: str | None
    """HTTP/3 的连接协议"""

    @property
    def is_webtransport(self) -> bool:
        """快速判断此次连接是否为 WebTransport 连接"""
        return self.method == "CONNECT" and self.protocol == "webtransport"

    @classmethod
    def from_header(cls, header: list[tuple[bytes, bytes]]) -> "HeaderInfo":
        """从 `aioquic` 的 `header` 中一次性解析出请求信息"""
        header_dict = dict((header.decode(), value.decode()) for header, value in header)
        target: URL = URL.build(scheme=header_dict[':scheme'], authority=header_dict[':authority'], path=header_dict[':path'])
        return HeaderInfo(target=target, method=header_dict[':method'], protocol=header_dict[':protocol'])


@dataclass(frozen=True)
class RouteInfo:
    """WebTransport 的路由信息"""

    handler_factory: HandlerFactory
    """"""

    kwargs: dict[str, Any]
    """"""
