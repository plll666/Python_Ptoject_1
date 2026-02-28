import unittest
import logging
from src.logger import make_logger

class TestLogger(unittest.TestCase):
    def test_make_logger_creation(self):
        logger = make_logger("test_logger")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        
    def test_make_logger_handlers(self):
        logger = make_logger("test_logger_handlers")

        self.assertEqual(len(logger.handlers), 1)

        formatter = logger.handlers[0].formatter
        self.assertIsInstance(formatter, logging.Formatter)

        self.assertEqual(logger.level, logging.INFO)

if __name__ == "__main__":
    unittest.main()