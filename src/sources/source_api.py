from src.logger import make_logger
from src.task_model import Task


logger = make_logger("API_logger")

class ApiSource:
    """Моделирует внешний API для получения задач"""

    def __init__(self, source_name: str, mock_data: list[dict] | None = None):
        self.source_name = source_name
        self.mock_data = mock_data or [
            {
                "id": "api_1",
                "description": "1",
                "priority": 5,
                "status": "new"
            },
            {
                "id": "api_2",
                "description": "2",
                "priority": 4,
                "status": "in_progress"
            },
            {
                "id": "api_3",
                "description": "4",
                "priority": 3,
                "status": "new"
            },
            {
                "id": "api_4",
                "description": "4",
                "priority": 2,
                "status": "completed"
            }
        ]

    def get_tasks(self) -> list[Task]:
        """
        Получает задачи из внешнего API (имитация)
        """
        tasks = []

        for item in self.mock_data:
            try:
                if not all(key in item for key in ["id", "description", "priority", "status"]):
                    logger.error(f"API data missing required fields: {item}")
                    continue

                task = Task(
                    id=item["id"],
                    description=item["description"],
                    priority=item["priority"],
                    status=item["status"]
                )
                tasks.append(task)
            except (ValueError, AttributeError) as e:
                logger.error(f"API data missing required fields: {item}")
                continue

        return tasks