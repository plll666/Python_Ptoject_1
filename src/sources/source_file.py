from typing import Optional

from src.logger import make_logger
from src.task_model import Task

logger = make_logger("SourceFileLogger")

class ParseError(Exception):
    """Ошибка парсинга содержимого txt файла"""
    pass

class FileSource:
    """Источник задач из txt файла"""
    VALID_STATUSES = {"new", "in_progress", "completed", "deleted"}

    def __init__(self, path: str, separator: str = ":") -> None:
        self.path = path
        self.separator = separator

    def _parse_line(self, line: str, line_number: int) -> Optional[Task]:
        """
        Парсит одну строку файла и создает задачу
        """
        line = line.strip()
        if not line:
            return None

        if self.separator not in line:
            logger.error(f"Line {line_number}: missing separator '{self.separator}'")
            return None

        parts = line.split(self.separator)
        if len(parts) != 4:
            logger.error(f"Line {line_number}: expected 4 fields, got {len(parts)}")
            return None

        task_id, description, priority_str, status = parts

        task_id = task_id.strip()
        description = description.strip()
        status = status.strip().lower()

        if not task_id:
            logger.error(f"Line {line_number}: empty task ID")
            return None

        try:
            priority = int(priority_str.strip())
        except ValueError:
            logger.error(f"Line {line_number}: invalid priority value '{priority_str}'")
            return None

        if status not in self.VALID_STATUSES:
            logger.error(f"Line {line_number}: invalid status '{status}'")
            return None

        try:
            return Task(
                id=task_id,
                description=description,
                priority=priority,
                status=status
            )
        except (ValueError, AttributeError) as e:
            logger.error(f"Line {line_number}: validation error - {e}")
            return None

    def get_tasks(self) -> list[Task]:
        """
        Парсит txt файл с задачами
        Формат файла: каждая строка содержит поля, разделенные self.separator
        id:description:priority:status
        """
        tasks = []

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, 1):
                    task = self._parse_line(line, line_number)
                    if task:
                        tasks.append(task)

            logger.info(f"Successfully parsed {len(tasks)} tasks from {self.path}")

        except FileNotFoundError:
            logger.error(f'File not found: {self.path}')
        except PermissionError:
            logger.error(f'Permission denied: {self.path}')
        except UnicodeDecodeError:
            logger.error(f'Invalid encoding in file: {self.path}')

        return tasks