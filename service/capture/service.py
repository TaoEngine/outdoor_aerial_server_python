import asyncio
import logging

from sounddevice import RawInputStream
from typing import Callable, Optional, Self

from service.capture.dataclass import BroadcastConfig

log = logging.getLogger(__name__)


class CaptureService:
    __instance: Optional[Self] = None

    def __new__(cls, **_) -> Self:
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config: BroadcastConfig) -> None:
        self.__config: BroadcastConfig = config
        """广播采集配置"""

        self.__clients: set[Callable] = set()
        """订阅广播采集服务的客户端们"""

        maxsize: int = self.__config.maxsize
        self.__queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=maxsize)
        """广播采集客户端队列"""

        self.__running: bool = False
        """广播采集服务是否启动"""

        self.__event: Optional[asyncio.Event] = None
        """广播采集服务协程同步"""

        self.__input: Optional[RawInputStream] = None
        """广播采集采集输入源"""

        self.__task: Optional[asyncio.Task] = None
        """广播采集服务任务控制"""

        self.__loop: Optional[asyncio.AbstractEventLoop] = None
        """针对 callback 的线程安全"""

    async def stream(self) -> None:
        if self.__running:
            return
        self.__running = True

        # sounddevice 非线程安全
        self.__loop = asyncio.get_running_loop()

        self.__event = asyncio.Event()

        self.__task = asyncio.create_task(self.__distribute())
        log.info("客户端分发服务启动")

        self.__input = RawInputStream(
            blocksize=self.__config.blocksize.value,
            channels=self.__config.channel.value,
            device=self.__config.device,
            dtype=self.__config.dtype.value,
            samplerate=self.__config.samplerate.value,
            callback=self.__callback,
        )
        self.__input.start()
        log.info("广播采集服务启动")

        # 等待 stop 被触发
        with self.__input:
            await self.__event.wait()

    def stop(self) -> None:
        if self.__input is not None:
            log.info("广播采集服务将被终止")
            self.__input.stop()
            self.__input.close()
            self.__input = None

        if self.__task is not None:
            log.info("客户端分发服务将被终止")
            self.__task.cancel()
            self.__task = None

        if self.__event is not None:
            self.__event.set()
            self.__event = None

        self.__running = False

    def __callback(self, indata: bytes, *_) -> None:
        if self.__loop is not None:
            self.__loop.call_soon_threadsafe(
                self.__queue.put_nowait, indata
            )

    async def __distribute(self) -> None:
        try:
            while self.__running:
                audio_frame = await self.__queue.get()
                if self.__clients:
                    await asyncio.gather(
                        *[
                            broadcast_client(audio_frame)
                            for broadcast_client in self.__clients
                        ],
                        return_exceptions=True,
                    )
                self.__queue.task_done()
        except asyncio.CancelledError:
            pass

    def subscribe(self, client: Callable) -> None:
        self.__clients.add(client)
        clients: int = self.__clients.__len__()
        log.info(f"有新的客户端加入分发服务 目前共 {clients} 个客户端")

    def unsubscribe(self, client: Callable) -> None:
        self.__clients.discard(client)
        clients: int = self.__clients.__len__()
        log.info(f"有客户端退出分发服务 目前剩 {clients} 个客户端")
