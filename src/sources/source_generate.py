from src.contracts import Task
from random import randint


class TasksGenerator:
    """источник задач, который генерирует их"""

    def get_tasks(self) -> list[Task]:
        """генерирует случайное количество задач, со случайным id"""
        tasks = []
        for a in range(randint(1,10)):
            tasks.append(Task(str(randint(0,100000)), f"task_№{a}"))
        return tasks


