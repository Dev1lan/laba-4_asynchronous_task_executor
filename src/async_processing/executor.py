import asyncio
import logging

from src.async_processing.async_queue import AsyncTaskQueue
from src.async_processing.handler_protocols import AsyncTaskHandler
from src.domain.task import Task


class AsyncTaskExecutor:
    """Асинхронный исполнитель задач"""

    def __init__(
        self,
        queue: AsyncTaskQueue,
        handler: AsyncTaskHandler,
        workers_count: int = 2,
    ) -> None:
        if workers_count <= 0:
            raise ValueError("workers_count must be positive")

        self._queue = queue
        self._handler = handler
        self._workers_count = workers_count

        self._workers: list[asyncio.Task[None]] = []
        self._is_running = False

        self._logger = logging.getLogger(__name__)

    async def __aenter__(self) -> "AsyncTaskExecutor":
        """Войти в контекст async with и подготовить executor к работе"""

        self._logger.info("Executor started")

        self._is_running = True

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """Выйти из контекста async with и корректно остановить worker-ы"""

        await self.stop()

        self._logger.info("Executor stopped")

    async def run(self) -> None:
        """Запустить worker-ы и дождаться обработки всех задач"""

        self._workers = [
            asyncio.create_task(
                self._worker(index + 1)
            )
            for index in range(self._workers_count)
        ]

        await self._queue.join()

    async def stop(self) -> None:
        """Остановить executor и все worker-ы"""

        self._is_running = False

        for worker in self._workers:
            worker.cancel()

        if self._workers:
            await asyncio.gather(
                *self._workers,
                return_exceptions=True,
            )

        self._workers.clear()

    async def _worker(self, worker_id: int) -> None:
        """Постоянно получать задачи из очереди и передавать их в обработку"""

        while self._is_running:
            try:
                task = await self._queue.get()

                await self._process_task(
                    task,
                    worker_id,
                )

            except asyncio.CancelledError:
                # воркер остановлен через cancel()
                break

    async def _process_task(
        self,
        task: Task,
        worker_id: int,
    ) -> None:
        """Обработать одну задачу и записать результат в лог"""

        try:
            self._logger.info(
                "Worker %s started task %s",
                worker_id,
                task.id,
            )

            await self._handler.handle(task)

            self._logger.info(
                "Worker %s completed task %s",
                worker_id,
                task.id,
            )

        except Exception as error:
            self._logger.error(
                "Worker %s failed task %s: %s",
                worker_id,
                task.id,
                error,
            )

            task.status = "failed"

        finally:
            self._queue.task_done()
