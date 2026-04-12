import pytest
from datetime import datetime
from typing import List
from src.task_model import Task
from src.task_queue import TaskQueue, TaskFilter, TaskIterator


class TestTaskQueue:
    def setup_method(self):
        self.tasks = [
            Task("1", "Task 1", 5, "new"),
            Task("2", "Task 2", 3, "in_progress"),
            Task("3", "Task 3", 1, "completed"),
            Task("4", "Task 4", 4, "new"),
            Task("5", "Task 5", 2, "deleted"),
        ]
        self.queue = TaskQueue(self.tasks)

    def test_init_creates_queue_with_tasks(self):
        assert len(self.queue) == 5
        assert self.queue[0].id == "1"
        assert self.queue[-1].id == "5"

    def test_len_returns_correct_number(self):
        assert len(self.queue) == 5
        empty_queue = TaskQueue([])
        assert len(empty_queue) == 0

    def test_getitem_returns_correct_task(self):
        task = self.queue[0]
        assert task.id == "1"
        assert task.priority == 5

    def test_getitem_raises_index_error_for_invalid_index(self):
        with pytest.raises(IndexError, match="Index 10 out of range"):
            self.queue[10]
        with pytest.raises(IndexError):
            self.queue[-10]

    def test_iter_returns_task_iterator(self):
        iterator = iter(self.queue)
        assert isinstance(iterator, TaskIterator)

    def test_iteration_returns_all_tasks(self):
        task_ids = [task.id for task in self.queue]
        assert task_ids == ["1", "2", "3", "4", "5"]

    def test_multiple_iterations_work_correctly(self):
        first_iter = [task.id for task in self.queue]
        second_iter = [task.id for task in self.queue]
        assert first_iter == second_iter == ["1", "2", "3", "4", "5"]

    def test_filter_returns_task_filter(self):
        filtered = self.queue.filter(lambda t: t.priority > 3)
        assert isinstance(filtered, TaskFilter)

    def test_filter_by_status_returns_correct_tasks(self):
        new_tasks = list(self.queue.filter_by_status("new"))
        assert len(new_tasks) == 2
        assert all(t.status == "new" for t in new_tasks)
        assert new_tasks[0].id == "1"
        assert new_tasks[1].id == "4"

    def test_filter_by_priority_returns_correct_tasks(self):
        high_priority = list(self.queue.filter_by_priority(4))
        assert len(high_priority) == 2
        assert all(t.priority >= 4 for t in high_priority)
        assert high_priority[0].id == "1"
        assert high_priority[1].id == "4"

    def test_filter_by_priority_with_threshold(self):
        priority_3 = list(self.queue.filter_by_priority(3))
        assert len(priority_3) == 3
        assert all(t.priority >= 3 for t in priority_3)

        priority_5 = list(self.queue.filter_by_priority(5))
        assert len(priority_5) == 1
        assert priority_5[0].id == "1"

    def test_chained_filters_work_correctly(self):
        filtered = self.queue.filter_by_status("new").filter(lambda t: t.priority >= 4)
        result = list(filtered)
        assert len(result) == 2
        assert all(t.status == "new" for t in result)
        assert all(t.priority >= 4 for t in result)

    def test_filter_does_not_modify_original_queue(self):
        original_ids = [task.id for task in self.queue]
        self.queue.filter_by_status("new")
        assert [task.id for task in self.queue] == original_ids

    def test_queue_works_with_empty_tasks(self):
        empty_queue = TaskQueue([])
        assert len(empty_queue) == 0
        assert list(empty_queue) == []
        assert list(empty_queue.filter_by_status("new")) == []


class TestTaskFilter:
    def setup_method(self):
        self.tasks = [
            Task("1", "Task 1", 5, "new"),
            Task("2", "Task 2", 3, "in_progress"),
            Task("3", "Task 3", 1, "completed"),
            Task("4", "Task 4", 4, "new"),
        ]
        self.filter = TaskFilter(self.tasks, lambda t: t.status == "new")

    def test_filter_returns_iterator(self):
        result = iter(self.filter)
        assert hasattr(result, "__next__")

    def test_filter_iteration_returns_matching_tasks(self):
        result = list(self.filter)
        assert len(result) == 2
        assert all(t.status == "new" for t in result)
        assert result[0].id == "1"
        assert result[1].id == "4"

    def test_filter_with_no_matches_returns_empty(self):
        empty_filter = TaskFilter(self.tasks, lambda t: t.priority > 10)
        assert list(empty_filter) == []

    def test_filter_chaining_combines_predicates(self):
        filtered = self.filter.filter(lambda t: t.priority >= 4)
        result = list(filtered)
        assert len(result) == 2
        assert result[0].id == "1"
        assert result[1].id == "4"

    def test_multiple_filter_chaining(self):
        filtered = self.filter.filter(lambda t: t.priority >= 3).filter(lambda t: t.priority < 5)
        result = list(filtered)
        assert len(result) == 1
        assert result[0].id == "4"
        assert result[0].priority == 4

    def test_filter_does_not_modify_source_list(self):
        original_ids = [t.id for t in self.tasks]
        list(self.filter.filter(lambda t: t.priority > 3))
        assert [t.id for t in self.tasks] == original_ids

    def test_filter_can_be_iterated_multiple_times(self):
        first_iter = list(self.filter)
        second_iter = list(self.filter)
        assert first_iter == second_iter

    def test_filter_with_complex_predicate(self):
        complex_filter = TaskFilter(
            self.tasks,
            lambda t: t.status in ["new", "in_progress"] and t.priority >= 3
        )
        result = list(complex_filter)
        assert len(result) == 3
        assert result[0].id == "1"
        assert result[1].id == "2"
        assert result[2].id == "4"


class TestTaskIterator:
    def setup_method(self):
        self.tasks = [
            Task("1", "Task 1", 5, "new"),
            Task("2", "Task 2", 3, "in_progress"),
        ]
        self.iterator = TaskIterator(self.tasks)

    def test_iterator_returns_self_from_iter(self):
        assert iter(self.iterator) is self.iterator

    def test_next_returns_tasks_in_order(self):
        assert next(self.iterator).id == "1"
        assert next(self.iterator).id == "2"

    def test_next_raises_stop_iteration_when_exhausted(self):
        next(self.iterator)
        next(self.iterator)
        with pytest.raises(StopIteration):
            next(self.iterator)

    def test_iterator_works_with_empty_list(self):
        empty_iterator = TaskIterator([])
        with pytest.raises(StopIteration):
            next(empty_iterator)

    def test_iterator_can_be_converted_to_list(self):
        result = list(self.iterator)
        assert len(result) == 2
        assert result[0].id == "1"
        assert result[1].id == "2"

    def test_separate_iterators_are_independent(self):
        iterator1 = TaskIterator(self.tasks)
        iterator2 = TaskIterator(self.tasks)
        assert next(iterator1).id == "1"
        assert next(iterator1).id == "2"
        assert next(iterator2).id == "1"
        assert next(iterator2).id == "2"


class TestIntegration:
    def setup_method(self):
        self.tasks = [
            Task("1", "Task 1", 5, "new"),
            Task("2", "Task 2", 3, "in_progress"),
            Task("3", "Task 3", 2, "new"),
            Task("4", "Task 4", 4, "completed"),
        ]
        self.queue = TaskQueue(self.tasks)

    def test_queue_supports_list_conversion(self):
        result = list(self.queue)
        assert len(result) == 4
        assert isinstance(result, list)

    def test_queue_supports_len_function(self):
        assert len(self.queue) == 4

    def test_filtered_queue_supports_list_conversion(self):
        filtered = self.queue.filter_by_status("new")
        result = list(filtered)
        assert len(result) == 2
        assert isinstance(result, list)

    def test_complex_filtering_scenario(self):
        result = list(
            self.queue
            .filter_by_status("new")
            .filter(lambda t: t.priority >= 3)
        )
        assert len(result) == 1
        assert result[0].id == "1"

    def test_queue_works_with_for_loop(self):
        collected = []
        for task in self.queue:
            collected.append(task.id)
        assert collected == ["1", "2", "3", "4"]

    def test_filter_works_with_for_loop(self):
        collected = []
        for task in self.queue.filter_by_priority(4):
            collected.append(task.id)
        assert collected == ["1", "4"]

    def test_nested_filters_preserve_lazy_evaluation(self):
        filtered = self.queue.filter_by_status("new").filter(lambda t: t.priority > 3)
        assert not isinstance(filtered, list)
        assert hasattr(filtered, "__iter__")

    def test_large_number_of_tasks(self):
        large_tasks = [Task(str(i), f"Task {i}", i % 5 + 1, "new") for i in range(1000)]
        large_queue = TaskQueue(large_tasks)
        assert len(large_queue) == 1000
        filtered = list(large_queue.filter_by_priority(5))
        assert len(filtered) == 200


class TestEdgeCases:
    def setup_method(self):
        self.tasks = [
            Task("1", "Task 1", 5, "new"),
            Task("2", "Task 2", 3, "in_progress"),
            Task("3", "Task 3", 1, "completed"),
            Task("4", "Task 4", 4, "deleted"),
        ]
        self.queue = TaskQueue(self.tasks)

    def test_task_with_none_description(self):
        task = Task("1", None, 3, "new")
        queue = TaskQueue([task])
        assert queue[0].description is None

    def test_filter_with_empty_queue(self):
        queue = TaskQueue([])
        assert list(queue.filter_by_status("new")) == []
        assert list(queue.filter_by_priority(5)) == []

    def test_multiple_filters_on_empty_queue(self):
        queue = TaskQueue([])
        result = list(queue.filter_by_status("new").filter(lambda t: t.priority > 3))
        assert result == []

    def test_filter_preserves_task_objects(self):
        filtered = list(self.queue.filter_by_status("new"))
        for task in filtered:
            assert isinstance(task, Task)
            assert hasattr(task, "id")
            assert hasattr(task, "status")
            assert hasattr(task, "priority")
            assert hasattr(task, "created_at")

    def test_queue_with_single_task(self):
        single_task = Task("1", "Single", 5, "new")
        queue = TaskQueue([single_task])
        assert len(queue) == 1
        assert list(queue)[0].id == "1"
        assert list(queue.filter_by_status("new"))[0].id == "1"
        assert list(queue.filter_by_status("completed")) == []

    def test_all_statuses_are_filterable(self):
        statuses = ["new", "in_progress", "completed", "deleted"]
        for status in statuses:
            filtered = list(self.queue.filter_by_status(status))
            for task in filtered:
                assert task.status == status