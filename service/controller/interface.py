from typing import Awaitable, Callable


ClientFn = Callable[[bytes], Awaitable[None]]