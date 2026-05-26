import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from src.domain.task import Task


class GeneratorSource:
    """Источник, который генерирует задачи программно"""

    def __init__(self, count: int) -> None:
        if count < 0:
            raise ValueError("count must be non-negative")
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(1, self.count + 1):
            yield Task(
                id=i,
                description=f"Generated task #{i}",
                priority=3,
                status="new",
                created_at=datetime.now(),
            )


class APISource:
    """API-заглушка"""

    def __init__(self, tasks_data: list[dict[str, Any]] | None = None) -> None:
        self._tasks_data = tasks_data or [
            {"id": 101, "payload": {"source": "api", "message": "task one"}},
            {"id": 102, "payload": {"source": "api", "message": "task two"}},
        ]

    def get_tasks(self) -> Iterable[Task]:
        result: list[Task] = []

        for item in self._tasks_data:
            payload = item["payload"]
            description = payload.get("message", "Task from API")

            result.append(
                Task(
                    id=item["id"],
                    description=description,
                    priority=2,
                    status="new",
                    created_at=datetime.now(),
                )
            )

        return result


class FileSource:
    """Источник, который читает задачи из JSON-файла"""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def get_tasks(self) -> Iterable[Task]:
        with self.file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        result: list[Task] = []

        for item in raw_data:
            payload = item["payload"]
            description = payload.get("message", "Task from file")

            result.append(
                Task(
                    id=item["id"],
                    description=description,
                    priority=1,
                    status="new",
                    created_at=datetime.now(),
                )
            )

        return result
    
