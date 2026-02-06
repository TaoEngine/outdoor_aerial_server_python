import asyncio
import logging
import threading
from pathlib import Path
import sys

from sounddevice import RawOutputStream

# Ensure project root is on sys.path when running this file directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from service.controller import CaptureConfig, CaptureDtype, CaptureSampleRate, FetchService, CaptureChannel  # noqa: E402

log = logging.getLogger(__name__)


class ByteRingBuffer:
    def __init__(self, max_bytes: int) -> None:
        self._lock = threading.Lock()
        self._buf = bytearray()
        self._max_bytes = max_bytes

    def push(self, data: bytes) -> None:
        if not data:
            return
        with self._lock:
            self._buf.extend(data)
            if len(self._buf) > self._max_bytes:
                overflow = len(self._buf) - self._max_bytes
                del self._buf[:overflow]

    def pop_into(self, out: memoryview) -> int:
        with self._lock:
            n = min(len(out), len(self._buf))
            if n:
                out[:n] = self._buf[:n]
                del self._buf[:n]
            return n


async def main() -> None:
    logging.basicConfig(level="INFO", format="%(name)s: %(message)s")

    config = CaptureConfig(
        device=0,
        samplerate=CaptureSampleRate.R48000,
        dtype=CaptureDtype.Bit16,
        channel=CaptureChannel.Stereo
    )
    fetch_service = FetchService(config=config)

    bytes_per_sample = 2 if config.dtype == CaptureDtype.Bit16 else 4
    max_buffer_seconds = 5
    max_buffer_bytes = (
        config.samplerate.value * config.channel.value * bytes_per_sample * max_buffer_seconds
    )
    buffer = ByteRingBuffer(max_bytes=max_buffer_bytes)

    def output_callback(outdata, frames, _time, status) -> None:
        if status:
            log.warning("output status: %s", status)
        view = memoryview(outdata).cast("B")
        written = buffer.pop_into(view)
        if written < len(view):
            view[written:] = b"\x00" * (len(view) - written)

    async def push(data: bytes) -> None:
        buffer.push(data)

    output_stream = RawOutputStream(
        samplerate=config.samplerate.value,
        channels=config.channel.value,
        dtype=config.dtype.value,
        callback=output_callback,
        blocksize=config.blocksize.value,
    )

    task = asyncio.create_task(fetch_service.start())
    fetch_service.subscribe(1, push)

    try:
        with output_stream:
            log.info("fetch playback started, press Ctrl+C to stop.")
            await asyncio.Event().wait()
    except KeyboardInterrupt:
        log.info("stopping...")
    finally:
        fetch_service.unsubscribe(1)
        fetch_service.stop()
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
