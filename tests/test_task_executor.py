import unittest
import asyncio

from src.async_module.async_executor import AsyncExecutor
from src.async_module.async_queue import AsyncTaskQueue
from src.task.task_model import Task


class MockHandler:
    """Мок-обработчик для тестирования."""

    def __init__(self):
        self.handle_task_calls = []
        self.should_raise = False

    async def handle_task(self, task: Task) -> None:
        self.handle_task_calls.append(task)
        if self.should_raise:
            raise Exception("Test exception")


class TestAsyncExecutor(unittest.IsolatedAsyncioTestCase):
    """Тесты для асинхронного исполнителя задач."""

    def test_init(self):
        """Тест инициализации исполнителя."""
        queue = AsyncTaskQueue()
        executor = AsyncExecutor(workers=2, queue=queue)
        self.assertEqual(executor._workers, 2)
        self.assertIs(executor._queue, queue)
        self.assertEqual(len(executor._handlers), 0)

    def test_init_default_queue(self):
        """Тест инициализации с дефолтной очередью."""
        executor = AsyncExecutor(workers=2)
        self.assertEqual(executor._workers, 2)
        self.assertIsInstance(executor._queue, AsyncTaskQueue)
        self.assertEqual(len(executor._handlers), 0)

    def test_init_with_queue_strategy(self):
        """Тест инициализации со стратегией очереди."""
        queue = AsyncTaskQueue(maxsize=100)
        executor = AsyncExecutor(workers=2, queue=queue)
        self.assertIs(executor._queue, queue)

    def test_init_with_timeout(self):
        """Тест инициализации с таймаутом."""
        queue = AsyncTaskQueue()
        executor = AsyncExecutor(workers=1, queue=queue, submit_timeout=5.0)
        self.assertEqual(executor._submit_timeout, 5.0)

    def test_register_handler_valid(self):
        """Тест регистрации валидного обработчика."""
        handler = MockHandler()
        executor = AsyncExecutor(workers=1)
        executor.register_handler(handler)
        self.assertEqual(len(executor._handlers), 1)
        self.assertEqual(executor._handlers[0], handler)

    def test_register_handlers_multiple(self):
        """Тест регистрации нескольких обработчиков."""
        h1, h2 = MockHandler(), MockHandler()
        executor = AsyncExecutor(workers=1)
        executor.register_handlers(h1, h2)
        self.assertEqual(len(executor._handlers), 2)
        self.assertEqual(executor._handlers[0], h1)
        self.assertEqual(executor._handlers[1], h2)

    def test_register_handler_invalid(self):
        """Тест регистрации невалидного обработчика."""

        class InvalidHandler:
            pass

        executor = AsyncExecutor(workers=1)
        with self.assertRaises(TypeError) as context:
            executor.register_handler(InvalidHandler())
        self.assertIn("не реализует TaskHandler", str(context.exception))

    async def test_submit_without_context(self):
        """Тест отправки задачи без контекстного менеджера."""
        executor = AsyncExecutor(workers=1)
        task = Task("1", "Test task", 1, "new")

        with self.assertRaises(RuntimeError) as context:
            await executor.submit(task)
        self.assertIn("Обработчики не зарегистрированы", str(context.exception))

    async def test_submit_and_process_task(self):
        """Тест отправки и обработки задачи."""
        handler = MockHandler()
        async with AsyncExecutor(workers=1) as executor:
            executor.register_handler(handler)

            task = Task("1", "Test task", 1, "new")
            await executor.submit(task)
            await executor.wait_all()

            self.assertEqual(len(handler.handle_task_calls), 1)
            self.assertEqual(handler.handle_task_calls[0].id, "1")

    async def test_multiple_tasks(self):
        """Тест обработки множества задач."""
        handler = MockHandler()
        async with AsyncExecutor(workers=2) as executor:
            executor.register_handler(handler)

            for i in range(5):
                await executor.submit(Task(str(i), f"task {i}", i % 5 + 1, "new"))

            await executor.wait_all()

            self.assertEqual(len(handler.handle_task_calls), 5)
            processed_ids = {task.id for task in handler.handle_task_calls}
            self.assertEqual(processed_ids, {str(i) for i in range(5)})

    async def test_multiple_handlers(self):
        """Тест обработки несколькими обработчиками."""
        h1, h2 = MockHandler(), MockHandler()
        async with AsyncExecutor(workers=1) as executor:
            executor.register_handlers(h1, h2)

            task = Task("1", "Test task", 1, "new")
            await executor.submit(task)
            await executor.wait_all()

            self.assertEqual(len(h1.handle_task_calls), 1)
            self.assertEqual(len(h2.handle_task_calls), 1)

    async def test_error_handling(self):
        """Тест обработки ошибок."""
        handler = MockHandler()
        handler.should_raise = True

        async with AsyncExecutor(workers=1) as executor:
            executor.register_handler(handler)

            task = Task("1", "Failing task", 1, "new")
            await executor.submit(task)
            await executor.wait_all()

            self.assertEqual(len(handler.handle_task_calls), 1)
            self.assertEqual(len(executor.errors), 1)

    async def test_context_manager(self):
        """Тест работы контекстного менеджера."""
        async with AsyncExecutor(workers=1) as executor:
            self.assertIsNotNone(executor._queue)
            self.assertEqual(len(executor._worker_tasks), 1)

    async def test_clear_errors(self):
        """Тест очистки ошибок."""
        handler = MockHandler()
        handler.should_raise = True

        async with AsyncExecutor(workers=1) as executor:
            executor.register_handler(handler)

            task = Task("1", "task 1", 1, "new")
            await executor.submit(task)
            await executor.wait_all()

            errors = executor.clear_errors()
            self.assertEqual(len(errors), 1)
            self.assertEqual(len(executor.errors), 0)

    async def test_submit_with_queue_full(self):
        """Тест отправки при полной очереди."""
        queue = AsyncTaskQueue(maxsize=1)
        queue.put_nowait("blocking")

        async with AsyncExecutor(workers=1, queue=queue) as executor:
            executor.register_handler(MockHandler())

            task = Task("1", "Test task", 1, "new")
            with self.assertRaises(TimeoutError):
                await executor._queue.put(task, timeout=0.001)

    async def test_priority_ordering(self):
        """Тест обработки задач по приоритету."""
        handler = MockHandler()
        async with AsyncExecutor(workers=1) as executor:
            executor.register_handler(handler)

            await executor._queue.put(Task("1", "task 1", 3, "new"), priority=3)
            await executor._queue.put(Task("2", "task 2", 1, "new"), priority=1)
            await executor._queue.put(Task("3", "task 3", 5, "new"), priority=5)
            await executor.wait_all()

            self.assertEqual(len(handler.handle_task_calls), 3)
            self.assertEqual(handler.handle_task_calls[0].id, "2")
            self.assertEqual(handler.handle_task_calls[1].id, "1")
            self.assertEqual(handler.handle_task_calls[2].id, "3")

    async def test_errors_property_returns_copy(self):
        """Тест что errors возвращает копию."""
        handler = MockHandler()
        handler.should_raise = True

        async with AsyncExecutor(workers=1) as executor:
            executor.register_handler(handler)

            task = Task("1", "task 1", 1, "new")
            await executor.submit(task)
            await executor.wait_all()

            errors = executor.errors
            errors.append(Exception("new"))
            self.assertEqual(len(executor.errors), 1)


class AsyncTaskQueueTests(unittest.IsolatedAsyncioTestCase):
    """Тесты для AsyncTaskQueue."""

    def test_queue_init(self):
        """Тест создания очереди."""
        queue = AsyncTaskQueue(maxsize=10)
        self.assertEqual(queue.qsize, 0)
        self.assertTrue(queue.empty)
        self.assertFalse(queue.full)

    def test_queue_with_maxsize(self):
        """Тест очереди с ограничением размера."""
        queue = AsyncTaskQueue(maxsize=2)
        self.assertEqual(queue.qsize, 0)
        self.assertFalse(queue.full)

    async def test_put_get(self):
        """Тест put и get операций."""
        queue = AsyncTaskQueue()
        await queue.put("task1", priority=1)
        self.assertEqual(queue.qsize, 1)

        item = await queue.get()
        self.assertEqual(item, "task1")
        queue.task_done()

    async def test_priority_get(self):
        """Тест приоритетного порядка."""
        queue = AsyncTaskQueue()
        await queue.put("low", priority=5)
        await queue.put("high", priority=1)
        await queue.put("medium", priority=3)

        self.assertEqual(await queue.get(), "high")
        queue.task_done()
        self.assertEqual(await queue.get(), "medium")
        queue.task_done()
        self.assertEqual(await queue.get(), "low")
        queue.task_done()

    async def test_join_waits_for_all(self):
        """Тест join ждёт завершения всех задач."""
        queue = AsyncTaskQueue()
        await queue.put("task1")
        await queue.put("task2")

        queue.task_done()
        queue.task_done()
        await queue.join()

    def test_put_nowait(self):
        """Тест немедленной постановки."""
        queue = AsyncTaskQueue()
        result = queue.put_nowait("task", priority=2)
        self.assertTrue(result)
        self.assertEqual(queue.qsize, 1)

    def test_put_nowait_full(self):
        """Тест немедленной постановки при полной очереди."""
        queue = AsyncTaskQueue(maxsize=1)
        queue.put_nowait("task1")
        result = queue.put_nowait("task2")
        self.assertFalse(result)

    async def test_get_timeout_error(self):
        """Тест таймаута при get."""
        queue = AsyncTaskQueue()

        with self.assertRaises(asyncio.TimeoutError):
            await queue.get(timeout=0.001)

    def test_full_queue(self):
        """Тест полной очереди."""
        queue = AsyncTaskQueue(maxsize=1)
        queue.put_nowait("task1")
        self.assertTrue(queue.full)


if __name__ == "__main__":
    unittest.main()