from pluggy import HookspecMarker
from typing import Any

hookspec = HookspecMarker("outdoor.aerial.sever")


class AgentSpec:
    """为插件开发暴露的 AI 代理接口模板"""

    @hookspec
    async def init_agent(self) -> None:
        """初始化 AI 代理"""
        ...

    @hookspec
    async def dispose_agent(self) -> None:
        """解除 AI 代理"""
        ...

    @hookspec
    async def request_multimodal(
        self,
        model: str,
        prompt: str,
        payload: bytes | None = None,
        system_prompt: str | None = None,
        temperature: float = 1,
        top_p: float = 1,
        max_tokens: int | None = None,
        extra_config: dict[str, Any] | None = None,
    ) -> str | None:
        """请求多模态 AI 并返回需要的文本。

        Args:
            model (str): 本次请求调用的模型名称
            prompt (str): 用于控制 AI 的主提示词
            payload (bytes): 可选的多模态输入负载
            system_prompt (str): 用于约束模型的系统提示词
            temperature (float): 采样温度
            top_p (float): 核采样阈值
            max_tokens (int): 允许的最大 token 数量
            extra_config (dict): 扩展 AI 的配置参数

        Returns:
            多模态模型的文本响应
        """
        ...

    @hookspec
    async def list_tools(self) -> list[dict[str, Any]]:
        """返回当前可被 AI 识别和调用的工具定义"""
        ...

    @hookspec
    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """按工具名执行工具并返回执行结果"""
        ...

    @hookspec
    async def request_image(
        self,
        model: str,
        prompt: str,
        size: tuple[int, int],
        refer: list[bytes] | None = None,
    ) -> bytes | None:
        """请求生图 AI 并返回图片二进制
        
        Args:
            model (str): 本次请求调用的模型名称
            prompt (str): 用于生图的主提示词
            size (tuple[int, int]): 生图的尺寸
            refer (list[bytes]): 生图参考图片

        Returns:
            生图 AI 生成的图片
        """
        ...
