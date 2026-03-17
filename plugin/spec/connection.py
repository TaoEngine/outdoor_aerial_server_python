from pluggy import HookspecMarker
from asyncio import Queue

hookspec = HookspecMarker("outdoor.aerial.sever")


class ConnectionSpec:
    """为插件开发暴露的连接模板"""

    @hookspec
    async def init_connection(self) -> None:
        """初始化连接"""
        ...

    @hookspec
    async def dispose_connection(self) -> None:
        """解除连接"""
        ...

    @hookspec
    async def entrypoint_broadcast(self, payload: Queue[bytes]) -> None:
        """广播端点"""
        ...
