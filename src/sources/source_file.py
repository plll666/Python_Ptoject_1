from src.logger import make_logger
from src.contracts import Task

logger = make_logger("SourceFileLogger")

class ParseError(Exception):
    """Ошибка парсинга содержимого txt файла"""
    pass

class FileSource:
    """Источник задач из txt файла"""
    def __init__(self, path: str, separator: str=":") -> None:
        self.path = path
        self.separator = separator

    def get_tasks(self) -> list[Task]:
        """Парсит txt файл, в котором построчно записаны id и payload через разделитель"""
        tasks = []
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        if self.separator not in line:
                            raise ParseError

                        id, payload = line.split(self.separator, 1)
                        if not id or id == "":
                            raise ParseError
                        tasks.append(Task(id, payload))

                    except ParseError:
                        logger.error(f"File cant parse on line: {line_number}")

        except FileNotFoundError:
            logger.error(f'File not found: {self.path}')

        return tasks

