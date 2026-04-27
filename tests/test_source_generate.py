import unittest
from src.sources.source_generate import TasksGenerator
from src.task.task_model import Task


class TestTasksGenerator(unittest.TestCase):
    """Тесты для генератора задач"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.generator = TasksGenerator()

    def test_get_tasks_returns_list(self):
        """Тест возврата списка задач"""
        tasks = self.generator.get_tasks()
        self.assertIsInstance(tasks, list)

    def test_get_tasks_returns_tasks(self):
        """Тест возврата объектов Task"""
        tasks = self.generator.get_tasks()

        for task in tasks:
            self.assertIsInstance(task, Task)

    def test_get_tasks_has_all_attributes(self):
        """Тест наличия всех атрибутов задачи"""
        tasks = self.generator.get_tasks()

        for task in tasks:
            self.assertTrue(hasattr(task, 'id'))
            self.assertTrue(hasattr(task, 'description'))
            self.assertTrue(hasattr(task, 'priority'))
            self.assertTrue(hasattr(task, 'status'))
            self.assertTrue(hasattr(task, 'created_at'))
            self.assertTrue(hasattr(task, 'is_active'))
            self.assertTrue(hasattr(task, 'is_high_priority'))

            self.assertIsNotNone(task.id)
            self.assertIsInstance(task.priority, int)
            self.assertIsInstance(task.status, str)
            self.assertIn(task.status, ["new", "in_progress", "completed", "deleted"])
            self.assertIn(task.priority, range(1, 6))

    def test_get_tasks_random_count(self):
        """Тест генерации случайного количества задач"""
        counts = set()
        for _ in range(20):
            tasks = self.generator.get_tasks()
            counts.add(len(tasks))

        self.assertGreater(len(counts), 1, "get_tasks should return different number of tasks")

    def test_generator_with_active_only(self):
        """Тест генерации только активных задач"""
        generator_active = TasksGenerator(generate_active_only=True)

        for _ in range(10):
            tasks = generator_active.get_tasks()
            for task in tasks:
                self.assertIn(task.status, ["new", "in_progress"])

    def test_generator_with_all_statuses(self):
        """Тест генерации всех возможных статусов"""
        statuses_seen = set()

        for _ in range(50):
            tasks = self.generator.get_tasks()
            for task in tasks:
                statuses_seen.add(task.status)

        self.assertEqual(statuses_seen, {"new", "in_progress", "completed", "deleted"})

    def test_generator_priority_range(self):
        """Тест генерации приоритетов в правильном диапазоне"""
        priorities_seen = set()

        for _ in range(30):
            tasks = self.generator.get_tasks()
            for task in tasks:
                self.assertGreaterEqual(task.priority, 1)
                self.assertLessEqual(task.priority, 5)
                priorities_seen.add(task.priority)

        self.assertEqual(priorities_seen, {1, 2, 3, 4, 5})

    def test_generator_description_not_empty(self):
        """Тест, что описание не пустое (если не None)"""
        tasks = self.generator.get_tasks()

        for task in tasks:
            if task.description is not None:
                self.assertGreater(len(task.description), 0)

    def test_generator_unique_ids(self):
        """Тест уникальности ID задач в одной генерации"""
        tasks = self.generator.get_tasks()
        ids = [task.id for task in tasks]

        self.assertEqual(len(ids), len(set(ids)))

    def test_generator_with_large_number(self):
        """Тест генерации большого количества задач"""
        original_randint = __import__('random').randint

        def mock_randint(a, b):
            return 50

        import random
        random.randint = mock_randint

        try:
            tasks = self.generator.get_tasks()
            self.assertLessEqual(len(tasks), 50)
            self.assertGreaterEqual(len(tasks), 0)
        finally:
            random.randint = original_randint


if __name__ == "__main__":
    unittest.main()