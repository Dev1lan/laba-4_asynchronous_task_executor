from __future__ import annotations

from datetime import datetime

from .exceptions import (
    InvalidCreatedAtError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError,
    InvalidTaskIdError,
)


class BaseDescriptor:
    """
    Базовый data descriptor
    Хранит имя внутреннего атрибута, в который записывается значение
    """

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value) -> None:
        raise NotImplementedError("Subclasses must implement __set__")


class TaskIdDescriptor(BaseDescriptor):
    """
    Дескриптор для id задачи
    Допускаются только целые положительные числа
    """

    def __set__(self, instance, value: int) -> None:
        if not isinstance(value, int):
            raise InvalidTaskIdError("Task id must be an integer")
        if value <= 0:
            raise InvalidTaskIdError("Task id must be greater than 0")
        setattr(instance, self.private_name, value)


class DescriptionDescriptor(BaseDescriptor):
    """
    Дескриптор для описания задачи
    Описание должно быть непустой строкой
    """

    def __set__(self, instance, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidDescriptionError("Description must be a string")

        normalized_value = value.strip()
        if not normalized_value:
            raise InvalidDescriptionError("Description must not be empty")

        setattr(instance, self.private_name, normalized_value)


class PriorityDescriptor(BaseDescriptor):
    """
    Дескриптор для приоритета задачи
    Допустимые значения: целые числа от 1 до 5
    """

    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    def __set__(self, instance, value: int) -> None:
        if not isinstance(value, int):
            raise InvalidPriorityError("Priority must be an integer")

        if not (self.MIN_PRIORITY <= value <= self.MAX_PRIORITY):
            raise InvalidPriorityError(
                f"Priority must be between {self.MIN_PRIORITY} and {self.MAX_PRIORITY}"
            )

        setattr(instance, self.private_name, value)


class StatusDescriptor(BaseDescriptor):
    """
    Дескриптор для статуса задачи
    Разрешены только заранее определенные статусы
    """

    ALLOWED_STATUSES = {"new", "in_progress", "done", "failed"}

    def __set__(self, instance, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidStatusError("Status must be a string")

        normalized_value = value.strip().lower()
        if normalized_value not in self.ALLOWED_STATUSES:
            raise InvalidStatusError(
                f"Status must be one of: {', '.join(sorted(self.ALLOWED_STATUSES))}"
            )

        setattr(instance, self.private_name, normalized_value)


class CreatedAtDescriptor(BaseDescriptor):
    """
    Дескриптор для времени создания задачи
    Допускается только объект datetime
    """

    def __set__(self, instance, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise InvalidCreatedAtError("created_at must be a datetime instance")

        setattr(instance, self.private_name, value)