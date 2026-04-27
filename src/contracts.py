from typing import Protocol, runtime_checkable
from src.task.task_model import Task

@runtime_checkable
class Source(Protocol):
    """Протокол, определяющий интерфейс для источников задач"""
    def get_tasks(self) -> list[Task]:
        """Получение список задач из источника"""
        ...

@runtime_checkable
class TaskHandler(Protocol):
    """Протокол, определяющий интерфейс для обработчиков задач"""
    async def handle_task(self, task: Task) -> None:
        """Обработка 1 задачи"""
        ...