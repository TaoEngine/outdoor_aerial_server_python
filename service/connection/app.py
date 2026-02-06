from starlette.applications import Starlette
from starlette.types import Scope, Receive, Send
from typing import Callable, Optional
from weakref import WeakValueDictionary


class StarletteWebTransport:
    """支持 WebTransport 的 Starlette 包装"""

    def __init__(self) -> None:
        self._wt_routes: WeakValueDictionary[str, Callable] = WeakValueDictionary()
        self._http_app: Starlette = Starlette()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Starlette 为 ASGI 准备的入口"""
        scope_type: str = scope["type"]
        if scope_type == "webtransport":
            handler: Optional[Callable] = self._wt_routes.get(scope["path"])
            if handler is None:
                await send({"type": "webtransport.close"})
            else:
                await handler(scope, receive, send)
        else:
            # 其他 Http 请求就让 Starlette 自行处理
            await self._http_app(scope, receive, send)

    def add_wt_route(self, path: str, handler: Callable) -> None:
        """注册 WebTransport 路由"""
        self._wt_routes[path] = handler

    def add_http_route(self, path: str, endpoint: Callable, methods=None) -> None:
        """注册普通 HTTP 路由"""
        self._http_app.add_route(path, endpoint, methods=methods)
