from random import randint, choice
from datetime import datetime

from src.task.task_model import Task
from src.logger import make_logger

logger = make_logger("TasksGeneratorLogger")
class TasksGenerator:
    """Источник задач, который генерирует их"""

    STATUSES = ["new", "in_progress", "completed", "deleted"]
    DESCRIPTIONS = [
        "Process user order",
        "Send email notification",
        "Update user statistics",
        "Backup database",
        "Clean temporary files",
        "Generate report",
        "Sync with external API",
        "Validate user input",
        "Process payment",
        "Update cache"
    ]

    def __init__(self, generate_active_only: bool = False):
        self.generate_active_only = generate_active_only

    def get_tasks(self) -> list[Task]:
        """
        Генерирует случайное количество задач (от 1 до 10) со случайными атрибутами
        """
        tasks = []
        num_tasks = randint(1, 10)

        for i in range(num_tasks):
            task_id = f"gen_{i + 1}_{datetime.now().timestamp()}"

            description = choice(self.DESCRIPTIONS)

            priority = randint(1, 5)

            if self.generate_active_only:
                status = choice(["new", "in_progress"])
            else:
                status = choice(self.STATUSES)

            try:
                task = Task(
                    id=task_id,
                    description=description,
                    priority=priority,
                    status=status
                )
                tasks.append(task)
            except (ValueError, AttributeError) as e:
                logger.error(f"Error generating task {task_id}: {e}")
                continue

        return tasks