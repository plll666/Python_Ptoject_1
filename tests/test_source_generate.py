import unittest
from src.sources.source_generate import TasksGenerator
from src.contracts import Task

class TestTasksGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = TasksGenerator()
    
    def test_get_tasks_returns_list(self):
        tasks = self.generator.get_tasks()
        
        self.assertIsInstance(tasks, list)
    
    def test_get_tasks_returns_tasks(self):
        tasks = self.generator.get_tasks()
        
        for task in tasks:
            self.assertIsInstance(task, Task)
    
    def test_get_tasks_has_id_and_payload(self):
        tasks = self.generator.get_tasks()
        
        for task in tasks:
            self.assertTrue(hasattr(task, 'id'))
            self.assertTrue(hasattr(task, 'payload'))
            self.assertIsNotNone(task.id)
            self.assertIsInstance(task.payload, str)
    
    def test_get_tasks_random_count(self):
        tasks1 = self.generator.get_tasks()
        tasks2 = self.generator.get_tasks()

        different_count = False
        for _ in range(10):
            tasks1 = self.generator.get_tasks()
            tasks2 = self.generator.get_tasks()
            if len(tasks1) != len(tasks2):
                different_count = True
                break
                
        self.assertTrue(different_count, "get_tasks should return different number of tasks")

if __name__ == "__main__":
    unittest.main()