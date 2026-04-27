import asyncio
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class AsyncTaskQueue(Generic[T]):
    """Асинхронная очередь задач с поддержкой приоритетов, таймаутов и повторных попыток."""

    def __init__(self, maxsize: int = 0) -> None:
        self._queue: asyncio.PriorityQueue[tuple[int, int, Any]] = asyncio.PriorityQueue(maxsize=maxsize)
        self._counter = 0
        self._pending_tasks = 0

    async def put(self, item: T | None, priority: int = 3, timeout: float | None = None) -> None:
        """Добавить элемент в очередь с указанным приоритетом."""
        if item is None:
            priority = 0
            self._counter += 1
            entry = (priority, self._counter, item)
            if timeout is not None:
                await asyncio.wait_for(self._queue.put(entry), timeout=timeout)
            else:
                await self._queue.put(entry)
            return

        if not 1 <= priority <= 5:
            priority = max(1, min(5, priority))

        self._pending_tasks += 1
        self._counter += 1
        entry = (priority, self._counter, item)

        if timeout is not None:
            await asyncio.wait_for(self._queue.put(entry), timeout=timeout)
        else:
            await self._queue.put(entry)

    async def get(self, timeout: float | None = None) -> T | None:
        """Получить элемент из очереди."""
        if timeout is not None:
            item = await asyncio.wait_for(self._queue.get(), timeout=timeout)
        else:
            item = await self._queue.get()

        if item is not None and len(item) == 3:
            _, _, value = item
            return value
        return None

    def task_done(self) -> None:
        """Отметить задачу как обработанную."""
        if self._pending_tasks > 0:
            self._pending_tasks -= 1
        self._queue.task_done()

    async def join(self) -> None:
        """Ожидать завершения всех задач в очереди."""
        await self._queue.join()

    @property
    def qsize(self) -> int:
        """Вернуть текущий размер очереди."""
        return self._queue.qsize()

    @property
    def empty(self) -> bool:
        """Проверить, пуста ли очередь."""
        return self._queue.empty()

    @property
    def full(self) -> bool:
        """Проверить, полна ли очередь."""
        return self._queue.full()

    def put_nowait(self, item: T | None, priority: int = 3) -> bool:
        """Добавить элемент без ожидания"""
        if item is None:
            priority = 0
            self._counter += 1
            try:
                self._queue.put_nowait((priority, self._counter, item))
                return True
            except asyncio.QueueFull:
                return False

        if not 1 <= priority <= 5:
            priority = max(1, min(5, priority))

        self._pending_tasks += 1
        self._counter += 1
        try:
            self._queue.put_nowait((priority, self._counter, item))
            return True
        except asyncio.QueueFull:
            self._counter -= 1
            self._pending_tasks -= 1
            return False