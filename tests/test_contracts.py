import unittest
from src.contracts import Source, Task
from src.task_model import Task as TaskModel


class TestTaskModel(unittest.TestCase):
    """Тесты для модели Task"""

    def test_task_creation_with_valid_data(self):
        """Тест создания задачи с корректными данными"""
        task = TaskModel(
            id="task_001",
            description="Process user order",
            priority=5,
            status="new"
        )

        self.assertEqual(task.id, "task_001")
        self.assertEqual(task.description, "Process user order")
        self.assertEqual(task.priority, 5)
        self.assertEqual(task.status, "new")
        self.assertIsNotNone(task.created_at)

    def test_task_creation_with_none_description(self):
        """Тест создания задачи с None в описании"""
        task = TaskModel(
            id="task_002",
            description=None,
            priority=3,
            status="in_progress"
        )

        self.assertIsNone(task.description)

    def test_task_creation_with_empty_description(self):
        """Тест создания задачи с пустым описанием"""
        task = TaskModel(
            id="task_003",
            description="",
            priority=2,
            status="completed"
        )

        self.assertEqual(task.description, "")

    def test_task_creation_invalid_id(self):
        """Тест создания задачи с некорректным ID"""
        with self.assertRaises(ValueError):
            TaskModel(
                id="",
                description="test",
                priority=3,
                status="new"
            )

        with self.assertRaises(ValueError):
            TaskModel(
                id="   ",
                description="test",
                priority=3,
                status="new"
            )

    def test_task_creation_invalid_priority(self):
        """Тест создания задачи с некорректным приоритетом"""
        with self.assertRaises(ValueError):
            TaskModel(
                id="task_001",
                description="test",
                priority=0,
                status="new"
            )

        with self.assertRaises(ValueError):
            TaskModel(
                id="task_001",
                description="test",
                priority=6,
                status="new"
            )

        with self.assertRaises(ValueError):
            TaskModel(
                id="task_001",
                description="test",
                priority="high",  # не int
                status="new"
            )

    def test_task_creation_invalid_status(self):
        """Тест создания задачи с некорректным статусом"""
        with self.assertRaises(ValueError):
            TaskModel(
                id="task_001",
                description="test",
                priority=3,
                status="invalid_status"
            )

        with self.assertRaises(ValueError):
            TaskModel(
                id="task_001",
                description="test",
                priority=3,
                status=""
            )

    def test_task_id_immutable(self):
        """Тест неизменяемости ID задачи"""
        task = TaskModel(
            id="task_001",
            description="test",
            priority=3,
            status="new"
        )

        with self.assertRaises(AttributeError):
            task.id = "task_002"

    def test_task_properties(self):
        """Тест свойств задачи"""
        task_active = TaskModel(
            id="task_001",
            description="test",
            priority=3,
            status="new"
        )
        self.assertTrue(task_active.is_active)

        task_completed = TaskModel(
            id="task_002",
            description="test",
            priority=3,
            status="completed"
        )
        self.assertFalse(task_completed.is_active)

        task_deleted = TaskModel(
            id="task_003",
            description="test",
            priority=3,
            status="deleted"
        )
        self.assertFalse(task_deleted.is_active)

        task_high_priority = TaskModel(
            id="task_004",
            description="test",
            priority=4,
            status="new"
        )
        self.assertTrue(task_high_priority.is_high_priority)

        task_low_priority = TaskModel(
            id="task_005",
            description="test",
            priority=2,
            status="new"
        )
        self.assertFalse(task_low_priority.is_high_priority)


class TestSourceProtocol(unittest.TestCase):
    """Тесты для протокола Source"""

    def test_source_protocol_with_valid_source(self):
        """Тест проверки валидного источника"""

        class MockSource:
            def get_tasks(self):
                return []

        self.assertTrue(isinstance(MockSource(), Source))

    def test_source_protocol_with_invalid_source(self):
        """Тест проверки невалидного источника"""

        class NonSource:
            def get_task(self):
                return []

        self.assertFalse(isinstance(NonSource(), Source))

    def test_source_protocol_with_wrong_return_type(self):
        """Тест источника с неправильным возвращаемым типом"""

        class WrongReturnSource:
            def get_tasks(self):
                return "not a list"

        self.assertTrue(isinstance(WrongReturnSource(), Source))

    def test_source_protocol_with_correct_task_model(self):
        """Тест источника, возвращающего правильные задачи"""

        class CorrectSource:
            def get_tasks(self):
                return [
                    TaskModel("id1", "desc1", 3, "new"),
                    TaskModel("id2", "desc2", 4, "in_progress")
                ]

        source = CorrectSource()
        self.assertTrue(isinstance(source, Source))

        tasks = source.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks[0], TaskModel)


if __name__ == "__main__":
    unittest.main()