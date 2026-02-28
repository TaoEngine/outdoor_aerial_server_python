"""WebTransport 相关枚举说明。"""

from enum import Enum


class H3Method(Enum):
    """
    HTTP/3 的连接请求方法。

    WebTransport 连接通常以 CONNECT 形式出现，其他 HTTP/3 请求归为普通请求。
    """

    CONNECT = True
    """点对点连接请求。"""

    HTTP3 = False
    """其他 HTTP/3 请求。"""


class H3Protocol(Enum):
    """
    HTTP/3 的连接协议。

    WebTransport 连接协议值为 `webtransport`，其他协议归类为 OTHERS。
    """

    WEBTRANSPORT = True
    """WebTransport 连接协议。"""

    OTHERS = False
    """其他连接协议。"""


class H3Scheme(Enum):
    """
    HTTP/3 的连接方案。

    WebTransport 以 https 为主，其他情况归类为 OTHERS。
    """

    HTTPS = True
    """安全的 HTTPS 连接。"""

    OTHERS = False
    """其他连接方案。"""
