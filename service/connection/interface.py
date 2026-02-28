from typing import Callable

from service.connection.handler import WebTransportHandler

HandlerFactory = Callable[..., WebTransportHandler]
StreamSendFn = Callable[[int, bytes, bool], None]
TransmitFn = Callable[[], None]