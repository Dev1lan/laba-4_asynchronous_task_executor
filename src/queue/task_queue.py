from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Callable
from src.domain.task import Task


class TaskQueueIterator:
    """Собственный итератор для очереди задач"""

    def __init__(self, tasks: list[Task]) -> None:
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> TaskQueueIterator:
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            raise StopIteration

        task = self._tasks[self._index]
        self._index += 1
        return task


class TaskQueue:
    """Очередь задач с поддержкой итерации и ленивых фильтров"""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        self._tasks: list[Task] = list(tasks) if tasks is not None else []

    def add(self, task: Task) -> None:
        self._tasks.append(task)

    def extend(self, tasks: Iterable[Task]) -> None:
        self._tasks.extend(tasks)

    def __iter__(self) -> Iterator[Task]:
        return TaskQueueIterator(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def __repr__(self) -> str:
        return f"TaskQueue(tasks={self._tasks!r})"

    def filter(self, predicate: Callable[[Task], bool]) -> Iterator[Task]:
        for task in self._tasks:
            if predicate(task):
                yield task

    def filter_by_status(self, status: str) -> Iterator[Task]:
        normalized_status = status.strip().lower()
        yield from self.filter(lambda task: task.status == normalized_status)

    def filter_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Iterator[Task]:
        for task in self._tasks:
            if min_priority is not None and task.priority < min_priority:
                continue
            if max_priority is not None and task.priority > max_priority:
                continue
            yield task

    def iter_ready(self) -> Iterator[Task]:
        yield from self.filter(lambda task: task.is_ready)

    def iter_completed(self) -> Iterator[Task]:
        yield from self.filter(lambda task: task.is_completed)