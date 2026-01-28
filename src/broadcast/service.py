import asyncio
from typing import Callable, Optional, Self
from sounddevice import RawInputStream

from dataclass import BroadcastConfig


class BroadcastService:
    __instance: Optional[Self] = None

    def __new__(cls, **_) -> Self:
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config: BroadcastConfig) -> None:
        self.__broadcast_config: BroadcastConfig = config
        """广播采集配置"""

        self.__broadcast_clients: set[Callable] = set()
        """订阅广播服务的客户端们"""

        maxsize: int = self.__broadcast_config.maxsize
        self.__broadcast_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=maxsize)
        """广播客户端队列"""

        self.__broadcast_start: bool = False
        """广播服务是否启动"""

        self.__broadcast_event: Optional[asyncio.Event] = None
        """广播服务协程同步"""

        self.__broadcast_input: Optional[RawInputStream] = None
        """广播采集输入源"""

        self.__broadcast_task: Optional[asyncio.Task] = None
        """广播服务任务控制"""

        self.__broadcast_callback: Optional[asyncio.AbstractEventLoop] = None
        """针对 callback 的线程安全"""

    async def stream(self) -> None:
        if self.__broadcast_start:
            return
        self.__broadcast_start = True

        # sounddevice 非线程安全
        self.__broadcast_callback = asyncio.get_running_loop()

        self.__broadcast_event = asyncio.Event()

        self.__broadcast_task = asyncio.create_task(self.__broadcast_distribute())

        self.__broadcast_input = RawInputStream(
            blocksize=self.__broadcast_config.blocksize.value,
            channels=self.__broadcast_config.channel.value,
            device=self.__broadcast_config.device,
            dtype=self.__broadcast_config.dtype.value,
            samplerate=self.__broadcast_config.samplerate.value,
            callback=self.__callback,
        )
        self.__broadcast_input.start()

        # 等待 stop 被触发
        with self.__broadcast_input:
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

    def __callback(self, indata: bytes, *_) -> None:
        if self.__broadcast_callback is not None:
            self.__broadcast_callback.call_soon_threadsafe(
                self.__broadcast_queue.put_nowait, indata
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

    def subscribe(self, client: Callable) -> None:
        self.__broadcast_clients.add(client)

    def unsubscribe(self, client: Callable) -> None:
        self.__broadcast_clients.discard(client)


if __name__ == "__main__":
    config = BroadcastConfig(device=0)
    broadcast = BroadcastService(config=config)

    async def broadcasting(broadcast_data: bytes):
        print(broadcast_data)

    try:
        broadcast.subscribe(broadcasting)
        asyncio.run(broadcast.stream())
    except KeyboardInterrupt:
        broadcast.unsubscribe(broadcasting)
        broadcast.stop()
