import logging
from typing import Awaitable, Callable

from aioquic.h3.connection import H3Connection
from aioquic.h3.events import WebTransportStreamDataReceived, HeadersReceived

from service.capture import CaptureService

log = logging.getLogger(__name__)


class BroadcastHandler:
    """WebTransport 广播处理器"""

    def __init__(self, h3: H3Connection, capture: CaptureService):
        self._h3 = h3
        self._capture = capture
        self._callbacks: dict[int, Callable[[bytes], Awaitable[None]]] = {}

    def handle_event(self, event) -> None:
        """处理 H3 事件"""
        if isinstance(event, HeadersReceived):
            self._on_connect(event.stream_id)

        elif isinstance(event, WebTransportStreamDataReceived):
            # 客户端关闭信号
            if event.stream_ended:
                self._on_close(event.stream_id)

    def _on_connect(self, stream_id: int) -> None:
        """WebTransport 连接建立"""

        async def send_audio(data: bytes) -> None:
            self._h3.send_data(stream_id, data, end_stream=False)

        self._callbacks[stream_id] = send_audio
        self._capture.subscribe(send_audio)

        log.info(f"流 {stream_id}: 开始广播，共 {len(self._callbacks)} 个流")

    def _on_close(self, stream_id: int) -> None:
        """WebTransport 连接关闭"""
        callback = self._callbacks.pop(stream_id, None)
        if callback:
            self._capture.unsubscribe(callback)
            log.info(f"流 {stream_id}: 停止广播，剩 {len(self._callbacks)} 个流")

    def close(self) -> None:
        """清理所有广播流"""
        for callback in self._callbacks.values():
            self._capture.unsubscribe(callback)
        self._callbacks.clear()
        log.info("广播处理器清理完成")
