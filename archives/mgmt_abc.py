from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, List, Self, Union

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


class INodeType(ABC):
    def __init__(self, op, value, dtype):
        self._op : str      = op
        self._value : Any   = value
        self._dtype : str   = dtype

    @property
    def op(self) -> str:
        return self._op

    @property
    def value(self) -> str:
        return self._value

    @property
    def dtype(self) -> str:
        return self._dtype

    @staticmethod
    def _raise_unsupported_ops(op: str, ops: List[str]) -> True:
        if op not in ops:
            raise ValueError(f"Operation '{op}' is not supported. Supported operations are: {', '.join(ops)}")
        return True

    @classmethod
    @abstractmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        pass

    def expr_str(self, other: str) -> str:
        if not self._op or not other:
            return ""
        return f"{other} {self._op} {self._value}"


class INode(ABC):
    def __init__(self, name, def_type, desc, fn_cb=None):
        self._name : str = name
        self._def_type : str = def_type
        self._desc : str = desc
        self._fn_cb : Callable = fn_cb

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def def_type(self) -> str:
        return self._def_type

    @property
    def desc(self) -> str:
        return self._desc
    
    @property
    def fn_cb(self) -> Callable:
        return self._fn_cb
    
    @classmethod
    @abstractmethod
    def parse_yaml(cls, data) -> Any:
        pass

    @abstractmethod
    def process(self, cmd_lst:List[str]) -> Any:
        pass

    def _validate_process_syntax(self, cmd, cmd_len=None) -> bool:
        def raise_msg(msg):
            return f"Invalid syntax: {msg}"

        if cmd_len and not cmd_len == len(cmd):
            raise SyntaxError(raise_msg(f"Length of command does not match length {cmd_len}"))
        if "=" not in cmd:
            raise SyntaxError(raise_msg(f"{cmd} does not contain '='"))
