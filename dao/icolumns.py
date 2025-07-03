
from typing import Callable, List, Any
from db import DatabaseColumn
from abc import ABC


class IDatabaseColumns(ABC):
    """Interface for columns enumeration class"""

    @classmethod
    def members(cls) -> List[Any]:
        pass

    @classmethod
    def values(cls) -> List[DatabaseColumn]:
        pass

    @classmethod
    def primary(cls) -> List[DatabaseColumn]:
        pass

    @staticmethod
    def primary_sort(col) -> Callable[[DatabaseColumn], str]:
        pass
