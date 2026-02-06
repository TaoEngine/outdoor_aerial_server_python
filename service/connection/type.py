from dataclasses import dataclass
from typing import Optional


@dataclass
class H3Header:
    method: Optional[str]
    """连接请求"""

    protocol: Optional[str]
    """连接协议"""

    scheme: Optional[str]
    """连接方法"""

    authority: Optional[str]
    """连接地址"""

    path: Optional[str]
    """连接端点"""

    @classmethod
    def from_header(cls, header: list[tuple[bytes, bytes]]):
        simply_header = dict(
            (header.decode(), value.decode()) for header, value in header
        )
        return H3Header(
            method=simply_header.get(":method"),
            protocol=simply_header.get(":protocol"),
            scheme=simply_header.get(":https"),
            authority=simply_header.get(":authority"),
            path=simply_header.get(":path"),
        )