from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeAlias

if TYPE_CHECKING:
    from service.connection.handler import WebTransportHandler

HandlerFactory: TypeAlias = Callable[..., "WebTransportHandler"]
StreamSendFn: TypeAlias = Callable[[int, bytes, bool], None]
TransmitFn: TypeAlias = Callable[[], None]
TransportPeerName: TypeAlias = tuple[str, int] | tuple[str, int, int, int]
