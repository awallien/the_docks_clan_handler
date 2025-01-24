from abc import ABC
from typing import Dict, Callable

class ICallbackMapper(ABC):
    def __init__(self):
        self._cbs: Dict[str, Callable] = dict()

    def register(self, cb_name: str, cb_fn: Callable):
        if cb_name in self._cbs:
            raise ValueError(f"Duplicate callbacks for {cb_name}")
        self._cbs[cb_name] = cb_fn

    def call(self, cb_str: str, **kwargs) -> bool:
        if cb_str not in self._cbs:
            raise ValueError(f"Callback does not exist: {cb_str}")
        return self._cbs[cb_str](**kwargs)