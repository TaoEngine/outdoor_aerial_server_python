from enum import Enum


class H3Method(Enum):
    """
    HTTP/3 的连接请求

    可以是普通 HTTP 中 `GET` `POST` `HEAD` `PUT` `DELETE` `OPTIONS` 的任意一种，
    但是在点对点连接比如 WebTransport 中也可以是特殊请求 `CONNECT`
    """

    CONNECT = True
    """点对点连接请求"""

    HTTP3 = False
    """其他 HTTP/3 请求"""


class H3Protocol(Enum):
    """
    HTTP/3 的连接协议

    建立点对点连接后才会为其赋值，表示建立在 HTTP/3 上的协议名称，
    WebTransport 的连接协议值为 `webtransport`
    """

    WEBTRANSPORT = True
    """WebTransport 连接协议"""

    OTHERS = False
    """其他连接协议"""


class H3Scheme(Enum):
    """
    HTTP/3 的连接方法
    
    HTTP/3 的连接方法那肯定是 `https` 啊，
    其他的可以直接归类到 Others 不用看了
    """

    HTTPS = True
    """安全的 HTTPS 连接"""

    OTHERS = False
    """神鬼连接"""
