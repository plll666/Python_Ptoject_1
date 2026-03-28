import unittest
import tempfile
import os
from src.sources.source_file import FileSource, ParseError
from src.task_model import Task


class TestFileSource(unittest.TestCase):
    """Тесты для файлового источника задач"""

    def setUp(self):
        """Создание временного файла для тестов"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        self.temp_file_path = self.temp_file.name

    def tearDown(self):
        """Удаление временного файла"""
        self.temp_file.close()
        if os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
            except PermissionError:
                pass

    def test_get_tasks_empty_file(self):
        """Тест чтения пустого файла"""
        self.temp_file.close()
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 0)

    def test_get_tasks_valid_format(self):
        """Тест чтения файла с корректным форматом"""
        self.temp_file.write("task_001:Process user order:5:new\n")
        self.temp_file.write("task_002:Send email notification:3:in_progress\n")
        self.temp_file.write("task_003:Update statistics:2:completed\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 3)
        self.assertIsInstance(tasks[0], Task)
        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[0].description, "Process user order")
        self.assertEqual(tasks[0].priority, 5)
        self.assertEqual(tasks[0].status, "new")

        self.assertEqual(tasks[1].id, "task_002")
        self.assertEqual(tasks[1].priority, 3)
        self.assertEqual(tasks[1].status, "in_progress")

    def test_get_tasks_different_separator(self):
        """Тест чтения файла с другим разделителем"""
        self.temp_file.write("task_001:Process user order:5:new\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[0].description, "Process user order")

    def test_get_tasks_with_spaces(self):
        """Тест чтения файла с пробелами вокруг полей"""
        self.temp_file.write("  task_001  :  Process order  :  5  :  new  \n")
        self.temp_file.write("task_002:Send email:3:in_progress  \n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "task_001")
        self.assertEqual(tasks[0].description, "Process order")
        self.assertEqual(tasks[0].priority, 5)
        self.assertEqual(tasks[0].status, "new")

    def test_get_tasks_missing_fields(self):
        """Тест чтения файла с недостающим количеством полей"""
        self.temp_file.write("task_001:Process order:5\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_002")

    def test_get_tasks_invalid_priority(self):
        """Тест чтения файла с некорректным приоритетом"""
        self.temp_file.write("task_001:Process order:invalid:new\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_002")

    def test_get_tasks_invalid_status(self):
        """Тест чтения файла с некорректным статусом"""
        self.temp_file.write("task_001:Process order:5:invalid_status\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_002")

    def test_get_tasks_empty_id(self):
        """Тест чтения файла с пустым ID"""
        self.temp_file.write(":Process order:5:new\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_002")

    def test_get_tasks_priority_out_of_range(self):
        """Тест чтения файла с приоритетом вне диапазона"""
        self.temp_file.write("task_001:Process order:0:new\n")
        self.temp_file.write("task_002:Send email:6:in_progress\n")
        self.temp_file.write("task_003:Valid task:3:new\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "task_003")

    def test_file_not_found(self):
        """Тест обработки отсутствующего файла"""
        source = FileSource("nonexistent_file.txt", ":")
        tasks = source.get_tasks()

        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 0)

    def test_get_tasks_with_comments_and_empty_lines(self):
        """Тест чтения файла с комментариями и пустыми строками"""
        self.temp_file.write("\n")
        self.temp_file.write("# This is a comment\n")
        self.temp_file.write("task_001:Process order:5:new\n")
        self.temp_file.write("\n")
        self.temp_file.write("task_002:Send email:3:in_progress\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 2)

    def test_get_tasks_large_file(self):
        """Тест чтения большого файла"""
        num_tasks = 100
        for i in range(num_tasks):
            self.temp_file.write(f"task_{i:03d}:Task description {i}:{i % 5 + 1}:new\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), num_tasks)

        for i in range(min(5, num_tasks)):
            self.assertEqual(tasks[i].id, f"task_{i:03d}")
            self.assertEqual(tasks[i].priority, i % 5 + 1)

    def test_parse_error_exception(self):
        """Тест исключения ParseError"""
        self.temp_file.write("task_001:Process order:5:new\n")
        self.temp_file.close()

        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()

        self.assertEqual(len(tasks), 1)


if __name__ == "__main__":
    unittest.main()