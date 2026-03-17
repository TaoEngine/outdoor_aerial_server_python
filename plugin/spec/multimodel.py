from pluggy import HookspecMarker
from typing import Any

from msgspec import Struct

hookspec = HookspecMarker("outdoor.aerial.sever")


class ModelConfig(Struct):
    """多模态 AI 代理相关设置"""

    model: str
    """本次请求调用的模型名称"""

    temperature: float = 1
    """模型采样温度"""

    top_p: float = 1
    """模型核采样阈值"""

    max_tokens: int | None = None
    """模型允许的最大 token 数量"""

    extra_config: dict[str, Any] | None = None
    """扩展 AI 的配置参数"""


class MultiModelSpec:
    """为插件开发暴露的多模态 AI 代理接口模板"""

    @hookspec
    async def init_multimodel(self) -> None:
        """初始化多模态 AI 代理"""
        ...

    @hookspec
    async def dispose_multimodel(self) -> None:
        """解除多模态 AI 代理"""
        ...

    @hookspec
    async def configure_multimodel(self, config: ModelConfig) -> None:
        """配置多模态 AI 代理"""
        ...

    @hookspec
    async def multimodel_request(self) -> ...:
        """请求多模态 AI 代理"""
        ...
