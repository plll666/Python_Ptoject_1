from typing import Protocol, runtime_checkable
from src.task_model import Task

@runtime_checkable
class Source(Protocol):
    """Протокол, определяющий интерфейс для источников задач"""
    def get_tasks(self) -> list[Task]:
        """Получение список задач из источника"""
        ...

