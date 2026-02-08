from dataclasses import dataclass
from typing import Optional
from urllib.parse import SplitResult, urlsplit

from service.connection.enum import H3Method, H3Protocol, H3Scheme


@dataclass(frozen=True)
class HeaderInfo:
    """HTTP/3 请求方发起的请求信息"""

    authority: SplitResult
    """HTTP/3 请求方请求的地址"""

    origin: SplitResult
    """HTTP/3 的请求方地址"""

    path: SplitResult
    """HTTP/3 的连接端点"""

    scheme: H3Scheme
    """HTTP/3 的连接方法"""

    method: Optional[H3Method]
    """HTTP/3 的连接请求"""

    protocol: Optional[H3Protocol]
    """HTTP/3 的连接协议"""

    @classmethod
    def from_header(cls, header: list[tuple[bytes, bytes]]) -> "HeaderInfo":
        """从 `aioquic` 的 `header` 中一次性解析出请求信息"""
        simply_header = dict(
            (header.decode(), value.decode()) for header, value in header
        )

        authority: SplitResult = urlsplit(simply_header[":authority"])
        origin: SplitResult = urlsplit(simply_header[":origin"])
        path: SplitResult = urlsplit(simply_header[":path"])

        match simply_header[":scheme"]:
            case "https":
                scheme: H3Scheme = H3Scheme.HTTPS
            case _:
                scheme: H3Scheme = H3Scheme.OTHERS
        match simply_header.get(":method"):
            case "CONNECT":
                method: Optional[H3Method] = H3Method.CONNECT
            case None:
                method: Optional[H3Method] = None
            case _:
                method: Optional[H3Method] = H3Method.HTTP3
        match simply_header.get(":protocol", "NONE"):
            case "webtransport":
                protocol: Optional[H3Protocol] = H3Protocol.WEBTRANSPORT
            case None:
                protocol: Optional[H3Protocol] = None
            case _:
                protocol: Optional[H3Protocol] = H3Protocol.OTHERS

        return HeaderInfo(
            authority=authority,
            origin=origin,
            path=path,
            scheme=scheme,
            method=method,
            protocol=protocol,
        )


@dataclass(frozen=True)
class SessionInfo:
    """WebTransport 一次连接事件中所含的信息"""

    session_id: int
    """请求方申请的连接 ID"""

    path: str 
    """请求方访问的端点""" # TODO 改为 SplitResult

    query_string: bytes 
    """""" # TODO 不知道干什么用的

    headers: list[tuple[bytes, bytes]]
    """请求方发起的请求信息""" # TODO 改为 HeaderInfo

    client: Optional[tuple[str, int] | str]
    """""" # TODO 不知道干什么用的
