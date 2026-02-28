from typing import Protocol, runtime_checkable
from dataclasses import dataclass

@dataclass
class Task:
    """Класс данных, представляющий задачу с идентификатором"""
    id: str
    payload: str

@runtime_checkable
class Source(Protocol):
    """Протокол, определяющий интерфейс для источников задач"""
    def get_tasks(self) -> list[Task]:
        """Получение список задач из источника"""
        ...

