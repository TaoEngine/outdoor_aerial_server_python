import asyncio
import logging

from sounddevice import RawInputStream
from typing import Awaitable, Callable, Optional, Self

from service.controller.dataclass import CaptureConfig

log = logging.getLogger(__name__)


class FetchService:
    """广播信号采集分发服务"""

    __instance: Optional[Self] = None

    def __new__(cls, **_) -> Self:
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config: Optional[CaptureConfig] = None) -> None:
        # 防止单例重复初始化
        if hasattr(self, "_FetchService__config"):
            return

        assert config, "CaptureService 没有在初始化时被配置"

        self.__config: CaptureConfig = config
        """广播信号采集配置"""

        self.__clients: dict[int, Callable[[bytes], Awaitable[None]]] = dict()
        """订阅服务的客户端们"""

        maxsize: int = self.__config.maxsize
        self.__queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=maxsize)
        """广播信号采集客户端队列"""

        self.__running: Optional[bool] = None
        """服务是否启动"""

        self.__event: Optional[asyncio.Event] = None
        """服务协程同步"""

        self.__input: Optional[RawInputStream] = None
        """输入源"""

        self.__task: Optional[asyncio.Task] = None
        """任务控制"""

        self.__loop: Optional[asyncio.AbstractEventLoop] = None
        """针对 `__callback` 的线程安全"""

    async def start(self) -> None:
        """初始化广播信号采集分发服务"""
        if self.__running:
            return
        self.__running = False

        # sounddevice 非线程安全，需要获取进程锁
        self.__loop = asyncio.get_running_loop()
        self.__input = RawInputStream(
            blocksize=self.__config.blocksize.value,
            channels=self.__config.channel.value,
            device=self.__config.device,
            dtype=self.__config.dtype.value,
            samplerate=self.__config.samplerate.value,
            callback=self.__callback,
        )
        self.__event = asyncio.Event()

        self.__input.start()
        log.info("广播信号采集服务已成功启动")

        self.__task = asyncio.create_task(self.__distribute())
        log.info("广播信号分发服务已成功启动")

        self.__running = True

        # 建立持续工作机制直至采集服务被结束
        with self.__input:
            await self.__event.wait()
            log.info("广播信号采集服务已被终止")

    def stop(self) -> None:
        """彻底结束广播信号采集分发服务"""
        self.__clients.clear()
        log.info("广播信号分发列表已被清空")

        if self.__input:
            self.__input.stop()
            self.__input.close()
            self.__input = None

        if self.__task:
            self.__task.cancel()
            self.__task = None

        if self.__event:
            self.__event.set()
            self.__event = None

        if self.__running:
            self.__running = None

    def __callback(self, indata: bytes, *_) -> None:
        """客户端分发的对象"""
        if self.__loop:
            self.__loop.call_soon_threadsafe(self.__queue.put_nowait, indata)

    async def __distribute(self) -> None:
        """采集广播信号后分发给客户端"""
        try:
            while self.__running:
                audio_frame = await self.__queue.get()
                if self.__clients:
                    await asyncio.gather(
                        *[
                            broadcast_client(audio_frame)
                            for broadcast_client in self.__clients.values()
                        ],
                        return_exceptions=True,
                    )
                self.__queue.task_done()
        except asyncio.CancelledError:
            log.info("广播信号分发服务已被终止")

    def subscribe(self, id: int, client: Callable[[bytes], Awaitable[None]]) -> None:
        """让客户端订阅广播信号采集分发服务"""
        self.__clients[id] = client
        log.info(f"有新的客户端加入分发服务 目前共 {self.__clients.__len__()} 个")

    def unsubscribe(self, id: int) -> None:
        """让客户端取消订阅广播信号采集分发服务"""
        try:
            self.__clients.pop(id)
            log.info(f"有客户端退出分发服务 目前剩 {self.__clients.__len__()} 个")
        except KeyError:
            log.warning(f"编号为 {id} 的客户端在尝试退出时出错")
