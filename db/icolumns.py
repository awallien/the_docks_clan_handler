
from typing import Callable, List, Any, Union
from abc import ABCMeta, abstractmethod
from enum import Enum, EnumMeta

class DatabaseColumn:
    """Database Column containing the name of the column and default value"""

    def __init__(self, name, default, dtype, categories=None):
        self._name : str        = name
        self._default : Any     = default

        # https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes
        self._dtype: Any        = dtype

        # only used if dtype is 'category'
        self._categories: List[Union[str, int]] = categories

        # Check if dtype is valid
        if self._dtype == "category":
            assert isinstance(self._categories, list) and \
                    all(isinstance(cat, (str, int)) for cat in self._categories), \
                    "`categories` must be a list of str or int if dtype is `category`"
    
    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default
        
    @property
    def dtype(self):
        return self._dtype
    
    @property
    def categories(self):
        return self._categories
    
    def query_expr(self, cmp_val, op) -> str:
        val = ''
        if self.dtype == "string":
            val = f"'{cmp_val}'"
        elif self.dtype == "datatime64[ns]":
            val = f""
        return f"({self.name} {op} {val})"
    
    def __eq__(self, value) -> bool:
        if not isinstance(value, DatabaseColumn):
            return False
        return (
            self.name == value.name and
            self.default == value.default and
            self.dtype == value.dtype and
            self.categories == self.categories
        )
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __repr__(self):
        return f"DatabaseColumn(name={self.name}, default={self.default}, dtype={self.dtype}, categories={self.categories})"


class IDatabaseColumnsMeta(ABCMeta, EnumMeta):
    """Metaclass combining ABCMeta and EnumMeta."""
    pass

class IDatabaseColumns(Enum, metaclass=IDatabaseColumnsMeta):
    """Interface for columns enumeration class."""

    @classmethod
    def members(cls) -> List[Any]:
        """Return all enum members."""
        return list(cls.__members__.keys())

    @classmethod
    def values(cls) -> List['DatabaseColumn']:
        """Return list of associated DatabaseColumn values."""
        return [field.value for field in cls]

    @classmethod
    @abstractmethod
    def primary(cls) -> List['DatabaseColumn']:
        """Return list of primary key columns."""
        pass

    @staticmethod
    @abstractmethod
    def primary_sort(col: 'DatabaseColumn') -> Callable[['DatabaseColumn'], str]:
        """Return a function that defines how to sort primary columns."""
        pass
