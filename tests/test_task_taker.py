import unittest
from unittest.mock import Mock, patch
from src.task_taker import TaskTaker
from src.contracts import Source
from src.task_model import Task


class TestTaskTaker(unittest.TestCase):
    """Тесты для TaskTaker"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.mock_source1 = Mock(spec=Source)
        self.mock_source2 = Mock(spec=Source)

        self.task1 = Task("task_001", "Process order", 5, "new")
        self.task2 = Task("task_002", "Send email", 3, "in_progress")
        self.task3 = Task("task_003", "Update stats", 2, "completed")

        self.mock_source1.get_tasks.return_value = [self.task1, self.task2]
        self.mock_source2.get_tasks.return_value = [self.task3]

        self.task_taker = TaskTaker([self.mock_source1, self.mock_source2])

    def test_receive_tasks_returns_all_tasks(self):
        """Тест получения всех задач из всех источников"""
        tasks = self.task_taker.receive_tasks()

        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[1].description, "Send email")
        self.assertEqual(tasks[2].status, "completed")

    def test_receive_tasks_skips_non_source(self):
        """Тест пропуска объектов, не реализующих протокол Source"""
        non_source = Mock()
        task_taker = TaskTaker([self.mock_source1, non_source, self.mock_source2])

        tasks = task_taker.receive_tasks()

        self.assertEqual(len(tasks), 3)
        non_source.get_tasks.assert_not_called()

    def test_receive_tasks_handles_wrong_return_type(self):
        """Тест обработки источника, возвращающего не список"""
        self.mock_source1.get_tasks.return_value = "not a list"

        tasks = self.task_taker.receive_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_003")

    def test_receive_tasks_handles_exception_in_get_tasks(self):
        """Тест обработки исключений в методе get_tasks"""
        self.mock_source1.get_tasks.side_effect = Exception("API connection error")

        tasks = self.task_taker.receive_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_003")

    def test_receive_tasks_empty_sources(self):
        """Тест с пустым списком источников"""
        task_taker = TaskTaker([])
        tasks = task_taker.receive_tasks()

        self.assertEqual(len(tasks), 0)

    def test_receive_tasks_with_one_source(self):
        """Тест с одним источником"""
        task_taker = TaskTaker([self.mock_source1])
        tasks = task_taker.receive_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[1].id, "task_002")

    def test_receive_tasks_with_source_returning_empty_list(self):
        """Тест с источником, возвращающим пустой список"""
        self.mock_source1.get_tasks.return_value = []

        tasks = self.task_taker.receive_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_003")

    def test_receive_tasks_with_source_returning_none(self):
        """Тест с источником, возвращающим None"""
        self.mock_source1.get_tasks.return_value = None

        tasks = self.task_taker.receive_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_003")

    @patch('src.task_taker.logger')
    def test_receive_tasks_logging(self, mock_logger):
        """Тест логирования в TaskTaker"""
        tasks = self.task_taker.receive_tasks()

        mock_logger.info.assert_called()
        mock_logger.error.assert_not_called()

    @patch('src.task_taker.logger')
    def test_receive_tasks_error_logging(self, mock_logger):
        """Тест логирования ошибок"""
        self.mock_source1.get_tasks.side_effect = Exception("Test error")

        tasks = self.task_taker.receive_tasks()

        mock_logger.error.assert_called()

    def test_receive_tasks_preserves_task_order(self):
        """Тест сохранения порядка задач"""
        task_taker = TaskTaker([self.mock_source1, self.mock_source2])
        tasks = task_taker.receive_tasks()

        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[1].id, "task_002")
        self.assertEqual(tasks[2].id, "task_003")


class TestTaskTakerIntegration(unittest.TestCase):
    """Интеграционные тесты TaskTaker с реальными источниками"""

    def setUp(self):
        """Подготовка тестовых данных"""
        from src.sources.source_api import ApiSource
        from src.sources.source_generate import TasksGenerator

        self.api_source = ApiSource("test_api")
        self.generate_source = TasksGenerator(generate_active_only=True)

    def test_integration_with_multiple_sources(self):
        """Интеграционный тест с несколькими источниками"""
        task_taker = TaskTaker([self.api_source, self.generate_source])
        tasks = task_taker.receive_tasks()

        self.assertGreaterEqual(len(tasks), 4)

        for task in tasks:
            self.assertIsInstance(task, Task)
            self.assertIsNotNone(task.id)
            self.assertIsInstance(task.priority, int)
            self.assertIn(task.status, ["new", "in_progress", "completed", "deleted"])


if __name__ == "__main__":
    unittest.main()