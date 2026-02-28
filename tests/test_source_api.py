import unittest
from src.sources.source_api import ApiSource
from src.contracts import Task

class TestApiSource(unittest.TestCase):
    def setUp(self):
        self.source = ApiSource("test_api")
    
    def test_get_tasks_returns_list(self):
        tasks = self.source.get_tasks()
        
        self.assertIsInstance(tasks, list)
        
    def test_get_tasks_returns_tasks(self):
        tasks = self.source.get_tasks()
        
        for task in tasks:
            self.assertIsInstance(task, Task)
    
    def test_get_tasks_task_content(self):
        tasks = self.source.get_tasks()
        
        expected_ids = ["api1", "api2", "api3"]
        expected_payloads = ["task1", "task2", "task3"]
        
        self.assertEqual(len(tasks), 3)
        
        for i, task in enumerate(tasks):
            self.assertEqual(task.id, expected_ids[i])
            self.assertEqual(task.payload, expected_payloads[i])

if __name__ == "__main__":
    unittest.main()