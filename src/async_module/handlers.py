import asyncio
from typing import Dict

from src.task.task_model import Task
from src.logger import make_logger

logger = make_logger(__name__)


class PrintHandler:
    """Обработчик для печати задач"""

    async def handle_task(self, task: Task) -> None:
        """Печатает задачу"""
        await asyncio.sleep(1)
        print(f"Handling task: {task.id} - {task.description} (priority: {task.priority}, status: {task.status})")


class LoggingHandler:
    """Обработчик для логирования задач"""

    async def handle_task(self, task: Task) -> None:
        """Логирует задачу"""
        await asyncio.sleep(0.5)
        logger.info(f"Processing task: {task.id} - {task.description}")


class StatsHandler:
    """Обработчик для сбора статистики"""

    def __init__(self):
        self.processed_count: int = 0
        self.high_priority_count: int = 0
        self.start_time: float | None = None

    async def handle_task(self, task: Task) -> None:
        """Обновляет статистику по задаче"""
        await asyncio.sleep(0.1)

        self.processed_count += 1
        if task.is_high_priority:
            self.high_priority_count += 1

        logger.info(f"Stats updated: processed={self.processed_count}, high_priority={self.high_priority_count}")


class RetryHandler:
    """Обработчик с логикой повторных попыток"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}

    async def handle_task(self, task: Task) -> None:
        """Обрабатывает задачу с повторными попытками при неудаче"""
        task_id = task.id
        retries = self.retry_counts.get(task_id, 0)

        try:
            await asyncio.sleep(0.3)

            if retries < 2:
                raise Exception(f"Simulated error for task {task_id}")

            logger.info(f"Task {task_id} processed successfully after {retries} retries")
            self.retry_counts.pop(task_id, None)

        except Exception as e:
            if retries < self.max_retries:
                self.retry_counts[task_id] = retries + 1
                logger.warning(f"Retry {retries + 1}/{self.max_retries} for task {task_id}: {e}")
                raise
            else:
                logger.error(f"Task {task_id} failed after {self.max_retries} retries: {e}")
                self.retry_counts.pop(task_id, None)
                raise


class FilterHandler:
    """Обработчик, который фильтрует задачи по критериям"""

    def __init__(self, min_priority: int = 3):
        self.min_priority = min_priority
        self.filtered_out_count = 0

    async def handle_task(self, task: Task) -> None:
        """Обрабатывает только задачи с приоритетом выше минимального"""
        await asyncio.sleep(0.2)

        if task.priority < self.min_priority:
            self.filtered_out_count += 1
            logger.debug(f"Task {task.id} filtered out (priority {task.priority} < {self.min_priority})")
            return

        logger.info(f"Task {task.id} processed (priority {task.priority} >= {self.min_priority})")