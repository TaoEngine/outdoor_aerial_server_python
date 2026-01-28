import asyncio
import numpy as np
from typing import Callable, Optional, Self
from sounddevice import InputStream


class BroadcastService:
    _instance: Optional[Self] = None

    def __new__(cls) -> Self:
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.__broadcast_clients: set[Callable] = set()
        """订阅广播服务的客户端们"""

        self.__broadcast_input: Optional[InputStream] = None
        """广播采集输入"""

        self.__broadcast_queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=99999)
        """广播队列"""

        self.__broadcast_start: bool = False
        """广播服务是否启动"""

        self.__broadcast_task: Optional[asyncio.Task] = None
        """广播服务任务控制"""

    def stream(self) -> None:
        if self.__broadcast_start:
            return
        self.__broadcast_start = True

        self.__broadcast_task = asyncio.create_task(self.__broadcast_distribute())

        self.__broadcast_input = InputStream(
            samplerate=44100,
            channels=2,
            dtype="float32",
            callback=self.__callback,
            blocksize=1024,
        )

        self.__broadcast_input.start()

    def stop(self) -> None:
        if self.__broadcast_input is not None:
            self.__broadcast_input.stop()
            self.__broadcast_input.close()
            self.__broadcast_input = None

        if self.__broadcast_task is not None:
            self.__broadcast_task.cancel()
            self.__broadcast_task = None

        self.__broadcast_start = False

    def __callback(self, capture: np.ndarray, frames: int, time, status) -> None:
        audio_frame = np.copy(capture)
        self.__broadcast_queue.put_nowait(audio_frame)

    async def __broadcast_distribute(self) -> None:
        """将音频分发到所需的客户端中"""
        try:
            while self.__broadcast_start:
                audio_frame = await self.__broadcast_queue.get()
                if self.__broadcast_clients:
                    await asyncio.gather(
                        *[
                            broadcast_client(audio_frame)
                            for broadcast_client in self.__broadcast_clients
                        ],
                        return_exceptions=True,
                    )
                self.__broadcast_queue.task_done()
        except asyncio.CancelledError:
            pass

    def subscribe(self, client) -> None:
        self.__broadcast_clients.add(client)

    def unsubscribe(self, client) -> None:
        self.__broadcast_clients.discard(client)
