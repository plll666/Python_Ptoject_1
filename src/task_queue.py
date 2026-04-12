from typing import Iterator, Callable

from src.task_model import Task
from src.logger import make_logger

logger = make_logger("TaskQueue")

class TaskQueue():
    """ Очередь задач"""

    def __init__(self, tasks: list[Task]) -> None:
        self._tasks = tasks

    def __iter__(self) -> Iterator[Task]:
        """Итерация по очереди задач"""
        return TaskIterator(self._tasks)

    def __getitem__(self, index: int) -> Task:
        """Индексация очереди задач"""
        if index >= len(self._tasks):
            raise IndexError(f"Index {index} out of range")
        return self._tasks[index]

    def __len__(self) -> int:
        """Возвращает количество задач в очереди."""
        return len(self._tasks)

    def filter(self, predicate: Callable[[Task], bool]) -> TaskFilter:
        """Фильтр с задающимся предикатом"""
        return TaskFilter(self._tasks, predicate)

    def filter_by_status(self, status: str) -> TaskFilter:
        """фильтрация по статусу"""
        return self.filter(lambda task: task.status == status)

    def filter_by_priority(self, priority: int) -> TaskFilter:
        """Фильтрация по приоритету"""
        return self.filter(lambda task: task.priority >= priority)



class  TaskFilter():
    """Ленивая фильтрация задач"""

    def __init__ (self, tasks: list[Task], predicate: Callable[[Task], bool]) -> None:
        self._tasks = tasks
        self.predicate = predicate

    def __iter__(self) -> Iterator[Task]:
        """Ленивый обход"""
        for task in self._tasks:
            if self.predicate(task):
                yield task

    def filter(self, predicate: Callable[[Task], bool]) -> TaskFilter:
        """Комбинирует текущий фильтр с новым"""
        old_predicate = self.predicate
        new_predicate = lambda task: old_predicate(task) and predicate(task)
        return TaskFilter(self._tasks, new_predicate)


class TaskIterator:
    """Отдельный итератор с явным управлением состоянием."""

    def __init__(self, tasks: list[Task]) -> None:
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> TaskIterator:
        return self

    def __next__(self) -> Task:
        """Возвращает следующий элемент или генерирует StopIteration."""
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task