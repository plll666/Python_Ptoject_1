from datetime import datetime
from typing import Any


class DataDescriptor:
    """Базовый data-дескриптор"""

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = f"_{name}"
        self.public_name = name

    def __get__(self, obj: Any, objtype: type = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj: Any, value: Any) -> None:
        self.validate(value)
        setattr(obj, self.private_name, value)

    def __delete__(self, obj: Any) -> None:
        if hasattr(obj, self.private_name):
            delattr(obj, self.private_name)

    def validate(self, value: Any) -> None:
        """Метод для переопределения в наследниках"""
        pass


class NonDataDescriptor:
    """Non-data дескриптор. """

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = f"_{name}"
        self.public_name = name

    def __get__(self, obj: Any, objtype: type = None) -> Any:
        if obj is None:
            return self

        if hasattr(obj, self.private_name):
            return getattr(obj, self.private_name)

        return self.get_default(obj)

    def get_default(self, obj: Any) -> Any:
        """Возвращает значение по умолчанию (может быть переопределён в наследниках)"""
        return None


class IdDescriptor(DataDescriptor):
    """Data-дескриптор для идентификатора (неизменяемый)"""

    def __set__(self, obj: Any, value: Any) -> None:
        self.validate(value)
        if hasattr(obj, self.private_name):
            raise AttributeError(f"{self.public_name} cannot be changed after initialization")
        setattr(obj, self.private_name, value)

    def validate(self, value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{self.public_name} must be a non-empty string")


class PriorityDescriptor(DataDescriptor):
    """Data-дескриптор для приоритета (всегда валидируется)"""

    def validate(self, value: Any) -> None:
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise ValueError(f"{self.public_name} must be an integer between 1 and 5")


class StatusDescriptor(DataDescriptor):
    """Data-дескриптор для статуса (всегда валидируется)"""

    VALID_STATUSES = {"new", "in_progress", "completed", "deleted"}

    def validate(self, value: Any) -> None:
        if not isinstance(value, str) or value not in self.VALID_STATUSES:
            raise ValueError(f"{self.public_name} must be one of {self.VALID_STATUSES}")


class DescriptionDescriptor(NonDataDescriptor):
    """
    Non-data дескриптор для описания.
    """

    def __get__(self, obj: Any, objtype: type = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)


class Task:
    """
    Класс задачи с использованием data и non-data дескрипторов.
    """
    id = IdDescriptor()
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    description = DescriptionDescriptor()

    def __init__(self, id: str, description: str | None, priority: int, status: str) -> None:
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self._created_at = datetime.now()

    @property
    def is_active(self) -> bool:
        """Задача активна (не завершена и не удалена)"""
        return self.status not in {"completed", "deleted"}

    @property
    def is_high_priority(self) -> bool:
        """Задача с высоким приоритетом (4 или 5)"""
        return self.priority >= 4

    @property
    def created_at(self) -> datetime:
        """Время создания задачи (только для чтения)"""
        return self._created_at

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, description={self.description!r}, priority={self.priority}, status={self.status!r})"



