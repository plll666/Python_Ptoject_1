import unittest
import tempfile
import os
from src.sources.source_file import FileSource
from src.contracts import Task


class TestFileSource(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file_path = self.temp_file.name
        
    def tearDown(self):
        self.temp_file.close()
        if os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
            except PermissionError:
                pass
    
    def test_get_tasks_empty_file(self):
        self.temp_file.close()
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 0)
    
    def test_get_tasks_valid_format(self):
        self.temp_file.write("id1:payload1\n")
        self.temp_file.write("id2:payload2\n")
        self.temp_file.write("id3:payload3\n")
        self.temp_file.close()
        
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()
        
        self.assertEqual(len(tasks), 3)
        self.assertIsInstance(tasks[0], Task)
        self.assertEqual(tasks[0].id, "id1")
        self.assertEqual(tasks[0].payload, "payload1")
    
    def test_get_tasks_different_separator(self):
        self.temp_file.write("id1|payload1\n")
        self.temp_file.write("id2|payload2\n")
        self.temp_file.close()
        
        source = FileSource(self.temp_file_path, "|")
        tasks = source.get_tasks()
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "id1")
        self.assertEqual(tasks[0].payload, "payload1")
    
    def test_get_tasks_missing_id(self):
        self.temp_file.write(":payload1\n")
        self.temp_file.close()
        
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()
        
        self.assertEqual(len(tasks), 0)
    
    def test_get_tasks_missing_payload(self):
        self.temp_file.write("id1:\n")
        self.temp_file.close()
        
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, "id1")
        self.assertEqual(tasks[0].payload, "")
    
    def test_get_tasks_invalid_format(self):
        self.temp_file.write("invalidline\n")
        self.temp_file.close()
        
        source = FileSource(self.temp_file_path, ":")
        tasks = source.get_tasks()
        
        self.assertEqual(len(tasks), 0)
    
    def test_file_not_found(self):
        source = FileSource("nonexistent.txt", ":")
        tasks = source.get_tasks()
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 0)

if __name__ == "__main__":
    unittest.main()