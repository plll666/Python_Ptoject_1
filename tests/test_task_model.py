import unittest
from datetime import datetime
from src.task.task_model import (
    Task,
    IdDescriptor,
    PriorityDescriptor,
    StatusDescriptor,
    DescriptionDescriptor,
    DataDescriptor,
    NonDataDescriptor
)


class TestDescriptorBase(unittest.TestCase):
    """Базовые тесты для дескрипторов"""

    def test_data_descriptor_has_set(self):
        """Проверка, что data-дескриптор имеет __set__"""
        self.assertTrue(hasattr(DataDescriptor, '__set__'))
        self.assertTrue(hasattr(IdDescriptor, '__set__'))
        self.assertTrue(hasattr(PriorityDescriptor, '__set__'))
        self.assertTrue(hasattr(StatusDescriptor, '__set__'))

    def test_non_data_descriptor_no_set(self):
        """Проверка, что non-data дескриптор не имеет __set__"""
        self.assertFalse(hasattr(NonDataDescriptor, '__set__'))
        self.assertFalse(hasattr(DescriptionDescriptor, '__set__'))

    def test_descriptor_returns_self_on_class_access(self):
        """Проверка, что при доступе через класс возвращается дескриптор"""
        self.assertIsInstance(Task.id, IdDescriptor)
        self.assertIsInstance(Task.priority, PriorityDescriptor)
        self.assertIsInstance(Task.status, StatusDescriptor)
        self.assertIsInstance(Task.description, DescriptionDescriptor)


class TestIdDescriptor(unittest.TestCase):
    """Тесты для IdDescriptor"""

    def test_valid_id_accepts_non_empty_string(self):
        """ID должен принимать непустые строки"""
        task = Task("task_001", "description", 3, "new")
        self.assertEqual(task.id, "task_001")

    def test_valid_id_accepts_string_with_spaces(self):
        """ID должен принимать строки с пробелами внутри"""
        task = Task("task with spaces", "description", 3, "new")
        self.assertEqual(task.id, "task with spaces")

    def test_id_rejects_empty_string(self):
        """ID не должен принимать пустые строки"""
        with self.assertRaises(ValueError) as context:
            Task("", "description", 3, "new")
        self.assertIn("non-empty string", str(context.exception))

    def test_id_rejects_whitespace_only(self):
        """ID не должен принимать строки только из пробелов"""
        with self.assertRaises(ValueError) as context:
            Task("   ", "description", 3, "new")
        self.assertIn("non-empty string", str(context.exception))

    def test_id_rejects_non_string(self):
        """ID не должен принимать не-строковые значения"""
        with self.assertRaises(ValueError):
            Task(123, "description", 3, "new")

    def test_id_cannot_be_changed_after_init(self):
        """ID не должен изменяться после инициализации"""
        task = Task("task_001", "description", 3, "new")

        with self.assertRaises(AttributeError) as context:
            task.id = "task_002"
        self.assertIn("cannot be changed", str(context.exception))

    def test_id_can_be_deleted(self):
        """ID можно удалить (хотя это может нарушить инварианты)"""
        task = Task("task_001", "description", 3, "new")
        del task.id
        self.assertNotIn("_id", task.__dict__)


class TestPriorityDescriptor(unittest.TestCase):
    """Тесты для PriorityDescriptor"""

    def test_valid_priority_accepts_values_1_to_5(self):
        """Приоритет должен принимать значения от 1 до 5"""
        for priority in range(1, 6):
            task = Task(f"task_{priority}", "desc", priority, "new")
            self.assertEqual(task.priority, priority)

    def test_priority_rejects_value_below_1(self):
        """Приоритет не должен принимать значения меньше 1"""
        with self.assertRaises(ValueError) as context:
            Task("task_001", "desc", 0, "new")
        self.assertIn("between 1 and 5", str(context.exception))

    def test_priority_rejects_value_above_5(self):
        """Приоритет не должен принимать значения больше 5"""
        with self.assertRaises(ValueError) as context:
            Task("task_001", "desc", 6, "new")
        self.assertIn("between 1 and 5", str(context.exception))

    def test_priority_rejects_non_integer(self):
        """Приоритет не должен принимать не-целые числа"""
        with self.assertRaises(ValueError):
            Task("task_001", "desc", "high", "new")

        with self.assertRaises(ValueError):
            Task("task_001", "desc", 3.5, "new")

    def test_priority_can_be_changed(self):
        """Приоритет можно изменять"""
        task = Task("task_001", "desc", 3, "new")
        task.priority = 5
        self.assertEqual(task.priority, 5)

    def test_priority_validation_on_change(self):
        """Изменение приоритета должно валидироваться"""
        task = Task("task_001", "desc", 3, "new")

        with self.assertRaises(ValueError):
            task.priority = 6


class TestStatusDescriptor(unittest.TestCase):
    """Тесты для StatusDescriptor"""

    VALID_STATUSES = {"new", "in_progress", "completed", "deleted"}

    def test_valid_status_accepts_allowed_values(self):
        """Статус должен принимать допустимые значения"""
        for status in self.VALID_STATUSES:
            task = Task("task_001", "desc", 3, status)
            self.assertEqual(task.status, status)

    def test_status_rejects_invalid_value(self):
        """Статус не должен принимать недопустимые значения"""
        with self.assertRaises(ValueError) as context:
            Task("task_001", "desc", 3, "invalid")
        self.assertIn("must be one of", str(context.exception))

    def test_status_rejects_empty_string(self):
        """Статус не должен принимать пустую строку"""
        with self.assertRaises(ValueError):
            Task("task_001", "desc", 3, "")

    def test_status_is_case_sensitive(self):
        """Статус чувствителен к регистру"""
        with self.assertRaises(ValueError):
            Task("task_001", "desc", 3, "NEW")

        with self.assertRaises(ValueError):
            Task("task_001", "desc", 3, "InProgress")

    def test_status_can_be_changed(self):
        """Статус можно изменять"""
        task = Task("task_001", "desc", 3, "new")
        task.status = "in_progress"
        self.assertEqual(task.status, "in_progress")

    def test_status_validation_on_change(self):
        """Изменение статуса должно валидироваться"""
        task = Task("task_001", "desc", 3, "new")

        with self.assertRaises(ValueError):
            task.status = "invalid_status"


class TestDescriptionDescriptor(unittest.TestCase):
    """Тесты для DescriptionDescriptor (non-data descriptor)"""

    def test_description_accepts_string(self):
        """Описание должно принимать строки"""
        task = Task("task_001", "Valid description", 3, "new")
        self.assertEqual(task.description, "Valid description")

    def test_description_accepts_none(self):
        """Описание может быть None"""
        task = Task("task_001", None, 3, "new")
        self.assertIsNone(task.description)

    def test_description_can_be_changed(self):
        """Описание можно изменять (non-data особенность)"""
        task = Task("task_001", "initial", 3, "new")
        task.description = "updated"
        self.assertEqual(task.description, "updated")

    def test_description_can_be_set_to_none(self):
        """Описание можно установить в None после создания"""
        task = Task("task_001", "initial", 3, "new")
        task.description = None
        self.assertIsNone(task.description)

    def test_description_does_not_validate_on_set(self):
        task = Task("task_001", "initial", 3, "new")
        task.description = 123  # type: ignore
        self.assertEqual(task.description, 123)

    def test_description_can_be_deleted(self):
        """Описание можно удалить"""
        task = Task("task_001", "description", 3, "new")
        del task.description
        self.assertIsNone(task.description)

    def test_description_returns_none_if_not_set(self):
        """Если описание не установлено, возвращается None"""
        task = Task("task_001", "temp", 3, "new")
        del task.description
        self.assertIsNone(task.description)


class TestTaskProperties(unittest.TestCase):
    """Тесты для свойств Task"""

    def test_created_at_is_readonly(self):
        """created_at должен быть только для чтения"""
        task = Task("task_001", "desc", 3, "new")

        self.assertIsInstance(task.created_at, datetime)

        with self.assertRaises(AttributeError):
            task.created_at = datetime.now()

    def test_created_at_is_set_on_creation(self):
        """created_at устанавливается при создании"""
        before = datetime.now()
        task = Task("task_001", "desc", 3, "new")
        after = datetime.now()

        self.assertGreaterEqual(task.created_at, before)
        self.assertLessEqual(task.created_at, after)

    def test_is_active_for_new_task(self):
        """Новая задача должна быть активной"""
        task = Task("task_001", "desc", 3, "new")
        self.assertTrue(task.is_active)

    def test_is_active_for_in_progress_task(self):
        """Задача в процессе должна быть активной"""
        task = Task("task_001", "desc", 3, "in_progress")
        self.assertTrue(task.is_active)

    def test_is_active_for_completed_task(self):
        """Завершённая задача не должна быть активной"""
        task = Task("task_001", "desc", 3, "completed")
        self.assertFalse(task.is_active)

    def test_is_active_for_deleted_task(self):
        """Удалённая задача не должна быть активной"""
        task = Task("task_001", "desc", 3, "deleted")
        self.assertFalse(task.is_active)

    def test_is_high_priority_for_low_priority(self):
        """Низкий приоритет (1-3) не считается высоким"""
        for priority in range(1, 4):
            task = Task(f"task_{priority}", "desc", priority, "new")
            self.assertFalse(task.is_high_priority)

    def test_is_high_priority_for_high_priority(self):
        """Высокий приоритет (4-5) считается высоким"""
        for priority in range(4, 6):
            task = Task(f"task_{priority}", "desc", priority, "new")
            self.assertTrue(task.is_high_priority)

    def test_is_active_updates_with_status_change(self):
        """is_active должен обновляться при изменении статуса"""
        task = Task("task_001", "desc", 3, "new")
        self.assertTrue(task.is_active)

        task.status = "completed"
        self.assertFalse(task.is_active)

        task.status = "in_progress"
        self.assertTrue(task.is_active)

    def test_is_high_priority_updates_with_priority_change(self):
        """is_high_priority должен обновляться при изменении приоритета"""
        task = Task("task_001", "desc", 3, "new")
        self.assertFalse(task.is_high_priority)

        task.priority = 5
        self.assertTrue(task.is_high_priority)

        task.priority = 2
        self.assertFalse(task.is_high_priority)


class TestTaskIndependence(unittest.TestCase):
    """Тесты независимости экземпляров Task"""

    def test_tasks_are_independent(self):
        """Разные задачи не должны влиять друг на друга"""
        task1 = Task("task_001", "desc1", 3, "new")
        task2 = Task("task_002", "desc2", 4, "in_progress")

        task1.priority = 5
        task2.status = "completed"

        self.assertEqual(task1.priority, 5)
        self.assertEqual(task2.priority, 4)
        self.assertEqual(task1.status, "new")
        self.assertEqual(task2.status, "completed")
        self.assertEqual(task1.id, "task_001")
        self.assertEqual(task2.id, "task_002")

class TestTaskRepr(unittest.TestCase):
    """Тесты строкового представления Task"""

    def test_repr_contains_all_fields(self):
        """__repr__ должен содержать все поля"""
        task = Task("task_001", "description", 3, "new")
        repr_str = repr(task)

        self.assertIn("task_001", repr_str)
        self.assertIn("description", repr_str)
        self.assertIn("3", repr_str)
        self.assertIn("new", repr_str)

    def test_repr_is_evaluable(self):
        """__repr__ должен быть достаточно информативным"""
        task = Task("task_001", "description", 3, "new")
        repr_str = repr(task)

        self.assertTrue(repr_str.startswith("Task("))
        self.assertTrue(repr_str.endswith(")"))
        self.assertIn("id=", repr_str)
        self.assertIn("description=", repr_str)
        self.assertIn("priority=", repr_str)
        self.assertIn("status=", repr_str)


if __name__ == "__main__":
    unittest.main()