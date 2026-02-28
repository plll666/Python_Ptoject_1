from src.sources.source_api import ApiSource
from src.sources.source_file import FileSource
from src.sources.source_generate import TasksGenerator
from src.task_taker import TaskTaker

def main() -> None:
    """
    Создаёт различные источники задач и передаёт их в TaskTaker.
    Выводит общее количество полученных задач
    """
    source_api = ApiSource("https://example.com/api")
    source_file = FileSource("ваш_файл.txt")
    source_generate = TasksGenerator()

    task_taker = TaskTaker([source_api, source_file, source_generate])
    all_tasks = task_taker.receive_tasks()

    print(f"Tasks was received: {len(all_tasks)}")


if __name__ == "__main__":
    main()


