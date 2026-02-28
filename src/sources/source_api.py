from src.contracts import Task


class ApiSource:
    """Моделирует внешний API для получения задач"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    def get_tasks(self) -> list[Task]:
        """Имитирует получение задач от внешнего API"""

        api_response = [
            {"id": "api1", "payload": "task1"},
            {"id": "api2", "payload": "task2"},
            {"id": "api3", "payload": "task3"},
        ]

        tasks = []
        for item in api_response:
            tasks.append(Task(
                id=item["id"],
                payload=item["payload"]
            ))

        return tasks