class TaskError(Exception):
    """
    Базовое исключение для модели Task. Pодитель для всех ошибок задачи
    """
    pass


class InvalidTaskIdError(TaskError):
    """
    Ошибка: некорректный идентификатор задачи
    """
    pass


class InvalidDescriptionError(TaskError):
    """
    Ошибка: некорректное описание задачи
    """
    pass


class InvalidPriorityError(TaskError):
    """
    Ошибка: некорректный приоритет задачи
    """
    pass


class InvalidStatusError(TaskError):
    """
    Ошибка: некорректный статус задачи
    """
    pass


class InvalidCreatedAtError(TaskError):
    """
    Ошибка: некорректное время создания задачи
    """
    pass