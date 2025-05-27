from abc import ABC
from typing import Dict, Callable

class ICallbackMapper(ABC):
    def __init__(self):
        self._cbs: Dict[str, Callable] = dict()

    def register(self, cb_fn: Callable):
        fn_name = cb_fn.__name__
        if fn_name in self._cbs:
            raise ValueError(f"Duplicate callbacks for {fn_name}")
        self._cbs[fn_name] = cb_fn

    def call(self, cb_str: str, **kwargs) -> bool:
        if cb_str not in self._cbs:
            raise ValueError(f"Callback does not exist: {cb_str}")
        return self._cbs[cb_str](**kwargs)
    
    def __contains__(self, item):
        return item in self._cbs
