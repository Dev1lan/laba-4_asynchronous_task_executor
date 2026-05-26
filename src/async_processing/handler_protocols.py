from typing import Protocol, runtime_checkable

from src.domain.task import Task


@runtime_checkable
class AsyncTaskHandler(Protocol):
    """Контракт для асинхронных обработчиков задач"""

    async def handle(self, task: Task) -> None:
        """Асинхронно обработать одну задачу"""
        ...
