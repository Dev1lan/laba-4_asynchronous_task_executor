from __future__ import annotations

import asyncio
from collections.abc import Sequence

from src.domain.task import Task

from .handler_protocols import AsyncTaskHandler


class MarkDoneHandler:
    """Базовый обработчик, который переводит задачу в статус done"""

    def __init__(self, delay_seconds: float = 0.0) -> None:
        self._delay_seconds = delay_seconds

    async def handle(self, task: Task) -> None:
        """Обработать задачу с опциональной задержкой"""
        task.status = "in_progress"

        if self._delay_seconds > 0:
            await asyncio.sleep(self._delay_seconds)

        task.status = "done"


class FailableHandler:
    """Переводит задачу в failed, если в описании есть специальный маркер"""

    def __init__(self, fail_on_substring: str = "fail") -> None:
        self._fail_on_substring = fail_on_substring.lower()

    async def handle(self, task: Task) -> None:
        """Обработать задачу с проверкой на условие ошибки"""
        task.status = "in_progress"

        if self._fail_on_substring in task.description.lower():
            task.status = "failed"
            return

        task.status = "done"


class CompositeHandler:
    """Последовательно применяет несколько обработчиков к одной задаче"""

    def __init__(self, handlers: Sequence[AsyncTaskHandler]) -> None:
        """Инициализировать композицию обработчиков"""
        if not handlers:
            raise ValueError("At least one handler is required")
        self._handlers = list(handlers)

    async def handle(self, task: Task) -> None:
        """Запустить обработчики по очереди и остановиться при статусе failed"""
        for handler in self._handlers:
            await handler.handle(task)
            
            if task.status == "failed":
                break
