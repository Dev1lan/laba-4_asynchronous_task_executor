from __future__ import annotations

import asyncio
from collections.abc import Iterable

from src.domain.task import Task


class AsyncTaskQueue:
    """Асинхронная очередь задач на основе asyncio.Queue"""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        """Инициализировать очередь и при необходимости заполнить начальными задачами"""
        self._queue: asyncio.Queue[Task] = asyncio.Queue()

        if tasks is not None:
            for task in tasks:
                self.put_nowait(task)

    async def put(self, task: Task) -> None:
        """Асинхронно добавить задачу в очередь"""
        await self._queue.put(task)

    def put_nowait(self, task: Task) -> None:
        """Добавить задачу в очередь без ожидания"""
        self._queue.put_nowait(task)

    async def get(self) -> Task:
        """Асинхронно получить задачу из очереди"""
        return await self._queue.get()

    def task_done(self) -> None:
        """Отметить задачу как обработанную"""
        self._queue.task_done()

    async def join(self) -> None:
        """Дождаться завершения обработки всех задач в очереди"""
        await self._queue.join()

    def empty(self) -> bool:
        """Проверить, пуста ли очередь"""
        return self._queue.empty()

    def qsize(self) -> int:
        """Вернуть текущее количество задач в очереди"""
        return self._queue.qsize()
