from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from dataclasses import dataclass
from logging import Logger
from typing import Any


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
        awaitable: Awaitable[Any]

    def __init__(
        self, max_concurrent_tasks: int, timeout: float | None = None, name: str | None = None, logger: Logger | None = None
    ) -> None:
        """
        :param max_concurrent_tasks: Maximum number of tasks that can run concurrently.
        :param timeout: Optional overall timeout in seconds for running all tasks.
        :param name: Optional name for the runner.
        :param logger: Optional logger for task exceptions.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be positive if specified.")
        self.max_concurrent_tasks: int = max_concurrent_tasks
        self.timeout: float | None = timeout
        self.name = name
        self.logger = logger
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._tasks: list[AsyncTaskRunner.Task] = []
        self._was_run: bool = False
        self._task_ids: set[str] = set()

    def add_task(
        self,
        task_id: str,
        awaitable: Awaitable[Any],
    ) -> None:
        """
        Adds a task to the runner that will be executed when run() is called.

        :param task_id: Unique identifier for the task.
        :param awaitable: The awaitable (coroutine) to execute.
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
        self._tasks.append(AsyncTaskRunner.Task(task_id, awaitable))

    def _task_name(self, task_id: str) -> str:
        return f"{self.name}-{task_id}" if self.name else task_id

    async def run(self) -> AsyncTaskRunner.Result:
        """
        Executes all added tasks with concurrency limited by the semaphore.
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
            async with self.semaphore:
                try:
                    res: Any = await task.awaitable
                    results[task.task_id] = res
                except Exception as e:
                    if self.logger:
                        self.logger.exception(f"Task '{self._task_name(task.task_id)}' raised an exception")
                    exceptions[task.task_id] = e

        # Create asyncio tasks for all runner tasks
        tasks = [asyncio.create_task(run_task(task), name=self._task_name(task.task_id)) for task in self._tasks]

        try:
            if self.timeout is not None:
                # Run with timeout
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=self.timeout)
            else:
                # Run without timeout
                await asyncio.gather(*tasks)
        except TimeoutError:
            # Cancel all running tasks on timeout
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Wait for tasks to complete cancellation
            await asyncio.gather(*tasks, return_exceptions=True)
            is_timeout = True

        is_ok: bool = (not exceptions) and (not is_timeout)
        return AsyncTaskRunner.Result(results=results, exceptions=exceptions, is_ok=is_ok, is_timeout=is_timeout)
