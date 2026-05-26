from src.sources.source_protocols import TaskSource
from src.domain.task import Task


def receive_tasks(source: TaskSource) -> list[Task]:
    """ Принять задачи из произвольного источника, удовлетворяющего контракту"""
    if not isinstance(source, TaskSource):
        raise TypeError("Object does not satisfy TaskSource protocol")

    return list(source.get_tasks())