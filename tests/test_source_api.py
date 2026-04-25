import unittest
from src.sources.source_api import ApiSource
from src.task.task_model import Task


class TestApiSource(unittest.TestCase):
    """Тесты для API источника задач"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.source = ApiSource("test_api")

    def test_get_tasks_returns_list(self):
        """Тест возврата списка задач"""
        tasks = self.source.get_tasks()
        self.assertIsInstance(tasks, list)

    def test_get_tasks_returns_tasks(self):
        """Тест возврата объектов Task"""
        tasks = self.source.get_tasks()

        for task in tasks:
            self.assertIsInstance(task, Task)

    def test_get_tasks_task_content(self):
        """Тест содержимого задач из API"""
        tasks = self.source.get_tasks()

        expected_data = [
            {"id": "api_1", "description": "Process API webhook payload", "priority": 5, "status": "new"},
            {"id": "api_2", "description": "Sync user data from external CRM", "priority": 4, "status": "in_progress"},
            {"id": "api_3", "description": "Generate monthly billing report", "priority": 3, "status": "new"},
            {"id": "api_4", "description": "Send daily digest emails", "priority": 2, "status": "completed"}
        ]

        self.assertEqual(len(tasks), 4)

        for i, task in enumerate(tasks):
            self.assertEqual(task.id, expected_data[i]["id"])
            self.assertEqual(task.priority, expected_data[i]["priority"])
            self.assertEqual(task.status, expected_data[i]["status"])

    def test_get_tasks_with_custom_mock_data(self):
        """Тест с пользовательскими мок-данными"""
        custom_data = [
            {"id": "custom_1", "description": "Custom task 1", "priority": 5, "status": "new"},
            {"id": "custom_2", "description": "Custom task 2", "priority": 3, "status": "in_progress"}
        ]

        source = ApiSource("test_api", mock_data=custom_data)
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "custom_1")
        self.assertEqual(tasks[0].priority, 5)
        self.assertEqual(tasks[1].status, "in_progress")

    def test_get_tasks_handles_invalid_data(self):
        """Тест обработки некорректных данных в API ответе"""
        invalid_data = [
            {"id": "valid_1", "description": "Valid task", "priority": 3, "status": "new"},
            {"id": "invalid_1", "description": "Invalid task"},
            {"id": "valid_2", "description": "Valid task 2", "priority": 4, "status": "in_progress"}
        ]

        source = ApiSource("test_api", mock_data=invalid_data)
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "valid_1")
        self.assertEqual(tasks[1].id, "valid_2")

    def test_get_tasks_default_mock_data(self):
        """Тест с дефолтными мок-данными"""
        source = ApiSource("test_api")
        tasks = source.get_tasks()

        self.assertGreater(len(tasks), 0)
        self.assertIsInstance(tasks[0], Task)


if __name__ == "__main__":
    unittest.main()