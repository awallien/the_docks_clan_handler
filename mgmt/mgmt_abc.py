from abc import ABC
from typing import Dict, Callable

class ICallbackMapper(ABC):
    def __init__(self):
        self._cbs: Dict[str, Callable] = dict()

    def register(self, cb_fn: Callable):
        fn_name = cb_fn.__name__
        if fn_name in self._cbs:
            raise ValueError(f"Duplicate callbacks for {fn_name}")
        self.__setitem__(fn_name, cb_fn)
    
    def __contains__(self, item):
        return item in self._cbs

    def __getitem__(self, item):
        if item not in self._cbs:
            raise KeyError(f"Callback {item} not found")
        return self._cbs[item]
    
    def __setitem__(self, key, value):
        if not callable(value):
            raise TypeError(f"Value for {key} must be callable")
        self._cbs[key] = value