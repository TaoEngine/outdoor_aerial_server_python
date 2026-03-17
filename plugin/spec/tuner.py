from pluggy import HookspecMarker

hookspec = HookspecMarker("outdoor.aerial.sever")

class TunerSpec:
    """为插件开发暴露的调谐器控制模板"""

    @hookspec
    async def init_tuner(self) -> None:
        """初始化调谐器"""
        ...

    @hookspec
    async def dispose_tuner(self) -> None:
        """解除调谐器"""
        ...

    @hookspec
    async def tune(self, freq: int) -> None:
        """调谐到指定频率"""
        ...

    @hookspec
    async def capture(self) -> bytes | None:
        """采集调谐器"""
        ...

    @hookspec
    async def request_rds(self) -> bytes:
        """请求调谐器的 RDS 信息"""
        ...