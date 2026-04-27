from src.contracts import Source
from src.logger import make_logger
from src.contracts import Task

logger = make_logger("TaskTakerLogger")

class TaskTaker():
    """прием источников задач, в виде списка"""
    def __init__(self, task_sources: list[Source]) -> None:
        self.task_sources = task_sources

    def receive_tasks(self) -> list:
        """Обрабатывает источники задач с проверкой контракта.
        Метод перебирает все источники задач и проверяет, соответствуют ли они
        контракту Source с помощью isinstance. Если источник соответствует контракту,
        вызывается его метод get_tasks() для получения задач
        """
        all_tasks: list[Task] = []
        for task_source in self.task_sources:
            if not isinstance(task_source, Source):
                logger.error(f'Task source {task_source} is not a Source')
                continue
            try:
                tasks = task_source.get_tasks()
            except Exception as e:
                logger.error(f"Exception while getting tasks from {e}")
                continue

            if not isinstance(tasks, list):
                logger.error(f'Task source {task_source} is not a list')
                continue

            all_tasks.extend(tasks)
            logger.info(f"from {task_source} was geted {len(tasks)} tasks")

        return all_tasks
