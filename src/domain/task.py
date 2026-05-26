from dataclasses import dataclass, field
from datetime import datetime

from .descriptors import (
    TaskIdDescriptor,
    DescriptionDescriptor,
    PriorityDescriptor,
    StatusDescriptor,
    CreatedAtDescriptor,
)


@dataclass
class Task:
    """
    Модель задачи с использованием dataclass и дескрипторов
    """

    id = TaskIdDescriptor()
    description = DescriptionDescriptor()
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    created_at = CreatedAtDescriptor()

    _id: int = field(init=False, repr=False)
    _description: str = field(init=False, repr=False)
    _priority: int = field(init=False, repr=False)
    _status: str = field(init=False, repr=False)
    _created_at: datetime = field(init=False, repr=False)

    def __init__(
        self,
        id: int,
        description: str,
        priority: int,
        status: str,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now()

    @property
    def is_ready(self) -> bool:
        return self.status == "new"

    @property
    def is_completed(self) -> bool:
        return self.status == "done"

    def __str__(self):
        return f"[{self.status}] {self.description} (priority={self.priority})"
    
    def __repr__(self) -> str:
        return (
        f"Task(id={self.id}, "
        f"description={self.description!r}, "
        f"priority={self.priority}, "
        f"status={self.status!r}, "
        f"created_at={self.created_at!r})"
    )