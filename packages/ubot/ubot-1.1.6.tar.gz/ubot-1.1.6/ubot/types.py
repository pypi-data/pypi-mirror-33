from typing import Any, Awaitable, Callable, Dict, Optional

Update = Dict[str, Any]
HandlerFn = Callable[[Update], Awaitable[Optional[Any]]]
HandlerDict = Dict[str, Any]
