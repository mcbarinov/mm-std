from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import anyio


class AsyncTaskRunner:
    """
    AsyncTaskRunner executes a batch of asynchronous tasks with controlled concurrency.
    Note: This runner is designed for one-time use. Create a new instance for each batch of tasks.
    """

    @dataclass
    class Result:
        results: dict[str, Any]  # Maps task_id to result
        exceptions: dict[str, Any]  # Maps task_id to exception (if any)
        is_ok: bool  # True if no exception and no timeout occurred
        is_timeout: bool  # True if at least one task was cancelled due to timeout

    @dataclass
    class Task:
        """Individual task representation"""

        task_id: str
        async_func: Callable[..., Awaitable[Any]]
        args: tuple[Any, ...]
        kwargs: dict[str, Any]

    def __init__(self, max_concurrent_tasks: int, timeout: float | None = None) -> None:
        """
        :param max_concurrent_tasks: Maximum number of tasks that can run concurrently.
        :param timeout: Optional overall timeout in seconds for running all tasks.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be positive if specified.")
        self.max_concurrent_tasks: int = max_concurrent_tasks
        self.timeout: float | None = timeout
        self.limiter: anyio.CapacityLimiter = anyio.CapacityLimiter(max_concurrent_tasks)
        self._tasks: list[AsyncTaskRunner.Task] = []
        self._was_run: bool = False
        self._task_ids: set[str] = set()

    def add_task(
        self,
        task_id: str,
        async_func: Callable[..., Awaitable[Any]],
        *args: object,
        **kwargs: object,
    ) -> None:
        """
        Adds a task to the runner that will be executed when run() is called.

        :param task_id: Unique identifier for the task.
        :param async_func: The asynchronous function to execute.
        :param args: Positional arguments for async_func.
        :param kwargs: Keyword arguments for async_func.
        :raises RuntimeError: If the runner has already been used.
        :raises ValueError: If task_id is empty or already exists.
        """
        if self._was_run:
            raise RuntimeError("This AsyncTaskRunner has already been used. Create a new instance for new tasks.")

        if not task_id:
            raise ValueError("Task ID cannot be empty")

        if task_id in self._task_ids:
            raise ValueError(f"Task ID '{task_id}' already exists. All task IDs must be unique.")

        self._task_ids.add(task_id)
        self._tasks.append(AsyncTaskRunner.Task(task_id, async_func, args, kwargs))

    async def run(self) -> AsyncTaskRunner.Result:
        """
        Executes all added tasks with concurrency limited by the capacity limiter.
        If a timeout is specified, non-finished tasks are cancelled.

        :return: AsyncTaskRunner.Result containing task results, exceptions, and flags indicating overall status.
        :raises RuntimeError: If the runner has already been used.
        """
        if self._was_run:
            raise RuntimeError("This AsyncTaskRunner instance can only be run once. Create a new instance for new tasks.")

        self._was_run = True
        results: dict[str, Any] = {}
        exceptions: dict[str, Any] = {}
        is_timeout: bool = False

        async def run_task(task: AsyncTaskRunner.Task) -> None:
            async with self.limiter:
                try:
                    res: Any = await task.async_func(*task.args, **task.kwargs)
                    results[task.task_id] = res
                except Exception as e:
                    exceptions[task.task_id] = e

        try:
            if self.timeout is not None:
                with anyio.fail_after(self.timeout):
                    async with anyio.create_task_group() as tg:
                        for task in self._tasks:
                            tg.start_soon(run_task, task)
            else:
                async with anyio.create_task_group() as tg:
                    for task in self._tasks:
                        tg.start_soon(run_task, task)
        except TimeoutError:
            is_timeout = True

        is_ok: bool = (not exceptions) and (not is_timeout)
        return AsyncTaskRunner.Result(results=results, exceptions=exceptions, is_ok=is_ok, is_timeout=is_timeout)
