from typing import Iterable, Protocol, runtime_checkable
from src.domain.task import Task


@runtime_checkable
class TaskSource(Protocol):
    """Контракт для любого источника задач"""

    def get_tasks(self) -> Iterable[Task]:
        """Вернуть итерируемую коллекцию задач"""
        pass

