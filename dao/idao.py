from abc import ABC, abstractmethod
from typing import Any, List, Optional

from entity import IEntity


class IDao(ABC):
    """Interface for DAO class"""

    @abstractmethod
    def add(self, obj: IEntity) -> bool:
        pass

    @abstractmethod
    def get(self, key: Any) -> Optional[IEntity]:
        pass

    @abstractmethod
    def update(self, obj: IEntity) -> bool:
        pass

    @abstractmethod
    def delete(self, key: Any) -> bool:
        pass

    @abstractmethod
    def get_all(self, filter_expr: str='') -> List[IEntity]:
        pass
