from __future__ import annotations
import asyncio

from src.async_processing.executor import AsyncTaskExecutor
from src.async_processing.handlers import FailableHandler, MarkDoneHandler, CompositeHandler
from src.async_processing.async_queue import AsyncTaskQueue
from src.sources import GeneratorSource
from src.sources.receiver import receive_tasks

def print_tasks(title: str, tasks: list) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for task in tasks:
        print(task)

async def demo_async_processing() -> None:
    tasks = receive_tasks(GeneratorSource(6))
    tasks[2].description = "fail this task"

    print_tasks("Before async processing", tasks)

    queue = AsyncTaskQueue(tasks)

    handler = CompositeHandler([
        FailableHandler(fail_on_substring="fail"),
        MarkDoneHandler(delay_seconds=0.5)
    ])

    async with AsyncTaskExecutor(
        queue=queue,
        handler=handler,
        workers_count=3,
    ) as executor:
        await executor.run()

    print_tasks("After async processing", tasks)

    completed = sum(1 for task in tasks if task.is_completed)
    failed = sum(1 for task in tasks if task.status == "failed")

    print(f"\nCompleted: {completed}")
    print(f"Failed: {failed}")

def main() -> None:
    asyncio.run(demo_async_processing())

if __name__ == "__main__":
    main()