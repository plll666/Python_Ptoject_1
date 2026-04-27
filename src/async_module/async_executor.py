import asyncio

from src.task.task_model import Task
from src.contracts import TaskHandler
from src.logger import make_logger
from src.async_module.async_queue import AsyncTaskQueue

logger = make_logger("AsyncExecutor")


class AsyncExecutor:
    """Асинхронный исполнитель задач с поддержкой контекстного менеджера."""

    def __init__(
        self,
        workers: int,
        queue: AsyncTaskQueue[Task] | None = None,
        submit_timeout: float | None = None
    ) -> None:
        self._workers = workers
        self._queue = queue or AsyncTaskQueue[Task]()
        self._handlers: list[TaskHandler] = []
        self._worker_tasks: list[asyncio.Task] = []
        self._errors: list[Exception] = []
        self._submit_timeout = submit_timeout

    def register_handler(self, handler: object) -> None:
        """Зарегистрировать один обработчик задач."""
        if not isinstance(handler, TaskHandler):
            raise TypeError(
                f"{handler} не реализует TaskHandler: ожидается async_module def handle_task(task)"
            )
        self._handlers.append(handler)

    def register_handlers(self, *handlers: object) -> None:
        """Зарегистрировать несколько обработчиков задач."""
        for handler in handlers:
            self.register_handler(handler)

    @property
    def errors(self) -> list[Exception]:
        """Получить список ошибок, возникших при обработке."""
        return self._errors.copy()

    def clear_errors(self) -> list[Exception]:
        """Очистить список ошибок и вернуть их."""
        errors = self._errors.copy()
        self._errors.clear()
        return errors

    async def submit(self, task: Task) -> None:
        """Отправить задачу на выполнение."""
        if not self._handlers:
            raise RuntimeError("Обработчики не зарегистрированы")

        priority = getattr(task, 'priority', 3)
        await self._queue.put(task, priority=priority, timeout=self._submit_timeout)

    async def wait_all(self) -> None:
        """Ожидать завершения всех задач в очереди."""
        await self._queue.join()

    async def _worker(self) -> None:
        """Worker для обработки задач из очереди."""
        while True:
            task = await self._queue.get()

            try:
                if task is None:
                    break

                for handler in self._handlers:
                    try:
                        await handler.handle_task(task)
                    except Exception as e:
                        self._errors.append(e)
                        logger.error(f"Ошибка при обработке задачи {task.id}: {e}")
            finally:
                self._queue.task_done()


    async def __aenter__(self) -> "AsyncExecutor":
        """Запустить исполнитель и его рабочие задачи."""
        self._worker_tasks = [
            asyncio.create_task(self._worker())
            for _ in range(self._workers)
        ]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Остановить исполнитель, отправив сигналы завершения."""
        for _ in range(self._workers):
            await self._queue.put(None)

        await asyncio.gather(*self._worker_tasks)

        return False