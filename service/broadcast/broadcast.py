import asyncio
import numpy as np
from typing import Callable, Optional, Self
from sounddevice import InputStream


class BroadcastService:
    __instance: Optional[Self] = None

    def __new__(cls) -> Self:
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        self.__broadcast_clients: set[Callable] = set()
        """订阅广播服务的客户端们"""

        self.__broadcast_queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=10)
        """广播客户端队列"""

        self.__broadcast_start: bool = False
        """广播服务是否启动"""

        self.__broadcast_event: Optional[asyncio.Event] = None
        """广播服务协程同步"""

        self.__broadcast_input: Optional[InputStream] = None
        """广播采集输入源"""

        self.__broadcast_task: Optional[asyncio.Task] = None
        """广播服务任务控制"""

    async def stream(self) -> None:
        if self.__broadcast_start:
            return
        self.__broadcast_start = True

        # sounddevice 非线程安全，需要挂锁
        self.__callback_loop = asyncio.get_running_loop()

        self.__broadcast_task = asyncio.create_task(self.__broadcast_distribute())

        self.__broadcast_input = InputStream(
            samplerate=44100,
            channels=2,
            dtype="float32",
            callback=self.__callback,
            blocksize=1024,
        )
        self.__broadcast_input.start()

        # 等待 stop 被触发
        self.__broadcast_event = asyncio.Event()
        await self.__broadcast_event.wait()

    def stop(self) -> None:
        if self.__broadcast_input is not None:
            self.__broadcast_input.stop()
            self.__broadcast_input.close()
            self.__broadcast_input = None

        if self.__broadcast_task is not None:
            self.__broadcast_task.cancel()
            self.__broadcast_task = None

        if self.__broadcast_event is not None:
            self.__broadcast_event.set()
            self.__broadcast_event = None

        self.__broadcast_start = False

    def __callback(self, capture: np.ndarray, frames: int, time, status) -> None:
        audio_frame = np.copy(capture)
        if self.__callback_loop is not None:
            self.__callback_loop.call_soon_threadsafe(
                self.__broadcast_queue.put_nowait, audio_frame
            )

    async def __broadcast_distribute(self) -> None:
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


if __name__ == "__main__":
    broadcast = BroadcastService()

    async def broadcasting(audio_frame: np.ndarray):
        print(f"已接收到大小为 {audio_frame.__len__()} 流")

    try:
        broadcast.subscribe(broadcasting)
        asyncio.run(broadcast.stream())
    except KeyboardInterrupt:
        broadcast.unsubscribe(broadcasting)
        broadcast.stop()
