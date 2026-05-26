import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from src.domain.exceptions import (
    InvalidCreatedAtError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError,
    InvalidTaskIdError,
)
from src.sources.source_protocols import TaskSource
from src.sources.receiver import receive_tasks
from src.sources import APISource, FileSource, GeneratorSource
from src.domain.task import Task
from src.queue.task_queue import TaskQueue


def make_task(
    task_id: int,
    description: str = "Task",
    priority: int = 3,
    status: str = "new",
) -> Task:
    return Task(
        id=task_id,
        description=description,
        priority=priority,
        status=status,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


def test_task_creation_success() -> None:
    created_at = datetime(2026, 4, 6, 12, 0, 0)

    task = Task(
        id=1,
        description="Test task",
        priority=3,
        status="new",
        created_at=created_at,
    )

    assert task.id == 1
    assert task.description == "Test task"
    assert task.priority == 3
    assert task.status == "new"
    assert task.created_at == created_at


def test_task_creation_without_created_at() -> None:
    task = Task(
        id=1,
        description="Task without explicit datetime",
        priority=2,
        status="new",
    )

    assert isinstance(task.created_at, datetime)


def test_task_str() -> None:
    task = Task(
        id=1,
        description="Write tests",
        priority=5,
        status="new",
    )

    assert str(task) == "[new] Write tests (priority=5)"


def test_task_is_ready_property() -> None:
    task = Task(
        id=1,
        description="Ready task",
        priority=2,
        status="new",
    )

    assert task.is_ready is True
    assert task.is_completed is False


def test_task_is_completed_property() -> None:
    task = Task(
        id=1,
        description="Done task",
        priority=4,
        status="done",
    )

    assert task.is_ready is False
    assert task.is_completed is True


def test_task_invalid_id_type() -> None:
    with pytest.raises(InvalidTaskIdError, match="Task id must be an integer"):
        Task(
            id="1",  # type: ignore[arg-type]
            description="Bad id type",
            priority=3,
            status="new",
        )


def test_task_invalid_id_value() -> None:
    with pytest.raises(InvalidTaskIdError, match="Task id must be greater than 0"):
        Task(
            id=0,
            description="Bad id value",
            priority=3,
            status="new",
        )


def test_task_invalid_description_type() -> None:
    with pytest.raises(InvalidDescriptionError, match="Description must be a string"):
        Task(
            id=1,
            description=123,  # type: ignore[arg-type]
            priority=3,
            status="new",
        )


def test_task_invalid_description_empty() -> None:
    with pytest.raises(InvalidDescriptionError, match="Description must not be empty"):
        Task(
            id=1,
            description="   ",
            priority=3,
            status="new",
        )


def test_task_description_is_stripped() -> None:
    task = Task(
        id=1,
        description="   padded description   ",
        priority=3,
        status="new",
    )

    assert task.description == "padded description"


def test_task_invalid_priority_type() -> None:
    with pytest.raises(InvalidPriorityError, match="Priority must be an integer"):
        Task(
            id=1,
            description="Bad priority type",
            priority="high",  # type: ignore[arg-type]
            status="new",
        )


def test_task_invalid_priority_value() -> None:
    with pytest.raises(InvalidPriorityError, match="Priority must be between 1 and 5"):
        Task(
            id=1,
            description="Bad priority value",
            priority=10,
            status="new",
        )


def test_task_invalid_status_type() -> None:
    with pytest.raises(InvalidStatusError, match="Status must be a string"):
        Task(
            id=1,
            description="Bad status type",
            priority=3,
            status=123,  # type: ignore[arg-type]
        )


def test_task_invalid_status_value() -> None:
    with pytest.raises(InvalidStatusError, match="Status must be one of:"):
        Task(
            id=1,
            description="Bad status value",
            priority=3,
            status="unknown",
        )


def test_task_status_is_normalized() -> None:
    task = Task(
        id=1,
        description="Normalized status",
        priority=3,
        status="  IN_PROGRESS  ",
    )

    assert task.status == "in_progress"


def test_task_invalid_created_at() -> None:
    with pytest.raises(
        InvalidCreatedAtError,
        match="created_at must be a datetime instance",
    ):
        Task(
            id=1,
            description="Bad datetime",
            priority=3,
            status="new",
            created_at="2026-04-06",  # type: ignore[arg-type]
        )


def test_task_descriptor_validates_on_assignment() -> None:
    task = Task(
        id=1,
        description="Initial task",
        priority=3,
        status="new",
    )

    task.description = "Updated task"
    task.priority = 5
    task.status = "done"

    assert task.description == "Updated task"
    assert task.priority == 5
    assert task.status == "done"
    assert task.is_completed is True


def test_task_descriptor_raises_on_invalid_assignment() -> None:
    task = Task(
        id=1,
        description="Initial task",
        priority=3,
        status="new",
    )

    with pytest.raises(InvalidPriorityError, match="Priority must be between 1 and 5"):
        task.priority = 0


def test_generator_source_is_task_source() -> None:
    source = GeneratorSource(count=3)

    assert isinstance(source, TaskSource)


def test_api_source_is_task_source() -> None:
    source = APISource()

    assert isinstance(source, TaskSource)


def test_file_source_is_task_source(tmp_path: Path) -> None:
    file_path = tmp_path / "tasks.json"
    file_path.write_text(
        json.dumps(
            [{"id": 1, "payload": {"source": "file", "message": "task from file"}}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    source = FileSource(file_path)

    assert isinstance(source, TaskSource)


def test_generator_source_returns_tasks() -> None:
    source = GeneratorSource(count=3)

    tasks = list(source.get_tasks())

    assert len(tasks) == 3
    assert all(isinstance(task, Task) for task in tasks)
    assert [task.id for task in tasks] == [1, 2, 3]
    assert [task.description for task in tasks] == [
        "Generated task #1",
        "Generated task #2",
        "Generated task #3",
    ]
    assert all(task.priority == 3 for task in tasks)
    assert all(task.status == "new" for task in tasks)


def test_api_source_returns_tasks() -> None:
    source = APISource()

    tasks = list(source.get_tasks())

    assert len(tasks) == 2
    assert tasks[0].id == 101
    assert tasks[0].description == "task one"
    assert tasks[0].priority == 2
    assert tasks[0].status == "new"

    assert tasks[1].id == 102
    assert tasks[1].description == "task two"
    assert tasks[1].priority == 2
    assert tasks[1].status == "new"


def test_file_source_returns_tasks(tmp_path: Path) -> None:
    data = [
        {"id": 1, "payload": {"source": "file", "message": "alpha task"}},
        {"id": 2, "payload": {"source": "file", "message": "beta task"}},
    ]
    file_path = tmp_path / "tasks.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    source = FileSource(file_path)
    tasks = list(source.get_tasks())

    assert len(tasks) == 2
    assert tasks[0].id == 1
    assert tasks[0].description == "alpha task"
    assert tasks[0].priority == 1
    assert tasks[0].status == "new"

    assert tasks[1].id == 2
    assert tasks[1].description == "beta task"
    assert tasks[1].priority == 1
    assert tasks[1].status == "new"


def test_receive_tasks_with_valid_source() -> None:
    source = APISource()

    tasks = receive_tasks(source)

    assert len(tasks) == 2
    assert all(isinstance(task, Task) for task in tasks)


def test_receive_tasks_with_invalid_source() -> None:
    class InvalidSource:
        pass

    with pytest.raises(TypeError, match="Object does not satisfy TaskSource protocol"):
        receive_tasks(InvalidSource())  # type: ignore[arg-type]


def test_generator_source_negative_count() -> None:
    with pytest.raises(ValueError, match="count must be non-negative"):
        GeneratorSource(count=-1)


def test_empty_queue():
    queue = TaskQueue()

    assert len(queue) == 0
    assert list(queue) == []
    assert bool(queue) is False


def test_queue_iteration():
    tasks = [
        make_task(1, "A", 1, "new"),
        make_task(2, "B", 2, "in_progress"),
        make_task(3, "C", 5, "done"),
    ]
    queue = TaskQueue(tasks)

    result_ids = [task.id for task in queue]

    assert result_ids == [1, 2, 3]


def test_queue_supports_repeated_iteration():
    queue = TaskQueue(
        [
            make_task(1, "A"),
            make_task(2, "B"),
        ]
    )

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == [1, 2]
    assert second_pass == [1, 2]


def test_add_task():
    queue = TaskQueue()

    queue.add(make_task(1, "First"))

    assert len(queue) == 1
    assert [task.id for task in queue] == [1]


def test_extend_queue():
    queue = TaskQueue()
    tasks = [make_task(1), make_task(2), make_task(3)]

    queue.extend(tasks)

    assert len(queue) == 3
    assert [task.id for task in queue] == [1, 2, 3]


def test_filter_by_status_is_lazy_and_correct():
    queue = TaskQueue(
        [
            make_task(1, status="new"),
            make_task(2, status="done"),
            make_task(3, status="new"),
        ]
    )

    result = queue.filter_by_status("new")

    assert isinstance(result, Iterator)
    assert [task.id for task in result] == [1, 3]


def test_filter_by_priority_min_only():
    queue = TaskQueue(
        [
            make_task(1, priority=1),
            make_task(2, priority=3),
            make_task(3, priority=5),
        ]
    )

    result_ids = [task.id for task in queue.filter_by_priority(min_priority=3)]

    assert result_ids == [2, 3]


def test_filter_by_priority_max_only():
    queue = TaskQueue(
        [
            make_task(1, priority=1),
            make_task(2, priority=3),
            make_task(3, priority=5),
        ]
    )

    result_ids = [task.id for task in queue.filter_by_priority(max_priority=3)]

    assert result_ids == [1, 2]


def test_filter_by_priority_range():
    queue = TaskQueue(
        [
            make_task(1, priority=1),
            make_task(2, priority=2),
            make_task(3, priority=3),
            make_task(4, priority=4),
            make_task(5, priority=5),
        ]
    )

    result_ids = [
        task.id for task in queue.filter_by_priority(min_priority=2, max_priority=4)
    ]

    assert result_ids == [2, 3, 4]


def test_iter_ready():
    queue = TaskQueue(
        [
            make_task(1, status="new"),
            make_task(2, status="in_progress"),
            make_task(3, status="done"),
        ]
    )

    result_ids = [task.id for task in queue.iter_ready()]

    assert result_ids == [1]


def test_iter_completed():
    queue = TaskQueue(
        [
            make_task(1, status="new"),
            make_task(2, status="done"),
            make_task(3, status="done"),
        ]
    )

    result_ids = [task.id for task in queue.iter_completed()]

    assert result_ids == [2, 3]


def test_queue_works_with_sum():
    queue = TaskQueue(
        [
            make_task(1, status="done"),
            make_task(2, status="new"),
            make_task(3, status="done"),
        ]
    )

    completed_count = sum(1 for task in queue if task.is_completed)

    assert completed_count == 2


def test_filter_generator_is_one_time_iterator():
    queue = TaskQueue(
        [
            make_task(1, status="new"),
            make_task(2, status="new"),
        ]
    )

    filtered = queue.filter_by_status("new")

    first_pass = [task.id for task in filtered]
    second_pass = [task.id for task in filtered]

    assert first_pass == [1, 2]
    assert second_pass == []

# python -m pytest - запуск тестов

def test_async_executor_marks_done_for_all_tasks():
    import asyncio
    from src.async_processing.async_queue import AsyncTaskQueue
    from src.async_processing.executor import AsyncTaskExecutor
    from src.async_processing.handlers import MarkDoneHandler

    tasks = [
        make_task(1, "A", status="new"),
        make_task(2, "B", status="new"),
        make_task(3, "C", status="new"),
    ]

    async def run() -> None:
        queue = AsyncTaskQueue(tasks)
        async with AsyncTaskExecutor(queue=queue, handler=MarkDoneHandler(), workers_count=2) as executor:
            await executor.run()

    asyncio.run(run())

    assert all(task.status == "done" for task in tasks)


def test_async_executor_marks_failed_by_condition():
    import asyncio
    from src.async_processing.async_queue import AsyncTaskQueue
    from src.async_processing.executor import AsyncTaskExecutor
    from src.async_processing.handlers import FailableHandler

    tasks = [
        make_task(1, "normal task", status="new"),
        make_task(2, "please FAIL this", status="new"),
    ]

    async def run() -> None:
        queue = AsyncTaskQueue(tasks)
        async with AsyncTaskExecutor(queue=queue, handler=FailableHandler(), workers_count=1) as executor:
            await executor.run()

    asyncio.run(run())

    assert tasks[0].status == "done"
    assert tasks[1].status == "failed"


def test_async_executor_invalid_workers_count():
    from src.async_processing.async_queue import AsyncTaskQueue
    from src.async_processing.executor import AsyncTaskExecutor
    from src.async_processing.handlers import MarkDoneHandler

    queue = AsyncTaskQueue()
    with pytest.raises(ValueError, match="workers_count must be positive"):
        AsyncTaskExecutor(queue=queue, handler=MarkDoneHandler(), workers_count=0)


def test_composite_handler_requires_at_least_one_handler():
    from src.async_processing.handlers import CompositeHandler

    with pytest.raises(ValueError, match="At least one handler is required"):
        CompositeHandler([])


def test_composite_handler_execution_chain():
    """Проверяет, что CompositeHandler вызывает обработчики по цепочке."""
    import asyncio
    from src.async_processing.async_queue import AsyncTaskQueue
    from src.async_processing.executor import AsyncTaskExecutor
    from src.async_processing.handlers import CompositeHandler, MarkDoneHandler, FailableHandler

    tasks = [
        make_task(1, "task to fail", status="new"),
        make_task(2, "normal task", status="new"),
    ]

    async def run() -> None:
        queue = AsyncTaskQueue(tasks)
        handler = CompositeHandler([
            FailableHandler(fail_on_substring="fail"),
            MarkDoneHandler()
        ])
        
        async with AsyncTaskExecutor(queue=queue, handler=handler, workers_count=2) as executor:
            await executor.run()

    asyncio.run(run())

    assert tasks[0].status == "failed"
    assert tasks[1].status == "done"