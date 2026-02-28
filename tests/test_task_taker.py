import unittest
from unittest.mock import Mock
from src.task_taker import TaskTaker
from src.contracts import Source, Task


class TestTaskTaker(unittest.TestCase):
    def setUp(self):
        self.mock_source1 = Mock(spec=Source)
        self.mock_source2 = Mock(spec=Source)

        self.mock_source1.get_tasks.return_value = [Task("1", "a"), Task("2", "b")]
        self.mock_source2.get_tasks.return_value = [Task("3", "c")]

        self.task_taker = TaskTaker([self.mock_source1, self.mock_source2])

    def test_receive_tasks_returns_all_tasks(self):
        tasks = self.task_taker.receive_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].id, "1")
        self.assertEqual(tasks[2].payload, "c")

    def test_receive_tasks_skips_non_source(self):
        non_source = Mock()
        task_taker = TaskTaker([self.mock_source1, non_source, self.mock_source2])
        tasks = task_taker.receive_tasks()
        self.assertEqual(len(tasks), 3)
        non_source.get_tasks.assert_not_called()

    def test_receive_tasks_handles_wrong_return_type(self):
        self.mock_source1.get_tasks.return_value = "not a list"
        tasks = self.task_taker.receive_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "3")

    def test_receive_tasks_handles_exception_in_get_tasks(self):
        self.mock_source1.get_tasks.side_effect = Exception("API error")
        tasks = self.task_taker.receive_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "3")