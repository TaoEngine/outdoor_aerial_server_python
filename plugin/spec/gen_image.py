from pluggy import HookspecMarker

hookspec = HookspecMarker("outdoor.aerial.sever")


class ImageGenSpec:
    """为插件开发暴露的生图 AI 接口模板"""

    @hookspec
    async def init_image_gen(self) -> None:
        """初始化生图 AI"""
        ...

    @hookspec
    async def dispose_image_gen(self) -> None:
        """解除使用生图 AI"""
        ...

    @hookspec
    async def image_gen_request(self) -> bytes:
        """请求生图 AI 生成相关图片"""
        ...

    @hookspec
    async def image_gen_query_cost(self) -> str:
        """查询生图 AI 的额度"""
        ...
