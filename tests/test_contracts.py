import unittest
from src.contracts import Task, Source

class TestTask(unittest.TestCase):
    def test_task_creation(self):
        task = Task(id="1", payload="test payload")
        self.assertEqual(task.id, "1")
        self.assertEqual(task.payload, "test payload")


class TestSourceProtocol(unittest.TestCase):
    def test_source_protocol(self):
        class MockSource:
            def get_tasks(self):
                return []
        
        self.assertTrue(isinstance(MockSource(), Source))

        class NonSource:
            def get_task(self):
                return []
        
        self.assertFalse(isinstance(NonSource(), Source))

if __name__ == "__main__":
    unittest.main()