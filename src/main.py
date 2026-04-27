from src.sources.source_api import ApiSource
from src.sources.source_file import FileSource
from src.sources.source_generate import TasksGenerator
from src.task.task_taker import TaskTaker
from src.async_module.async_executor import AsyncExecutor
from src.async_module.handlers import PrintHandler
import asyncio


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

    print(f"Tasks received: {len(all_tasks)}")

    async def run_async():
        async with AsyncExecutor(workers=2) as executor:
            executor.register_handler(PrintHandler())
            for task in all_tasks:
                await executor.submit(task)
            await executor.wait_all()
        print(f"Errors: {len(executor.errors)}")

    asyncio.run(run_async())


if __name__ == "__main__":
    main()