import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from typing import Any

import anyio

from mm_std.date import utc_now
from mm_std.types_ import Args, AsyncFunc, Kwargs


class AsyncScheduler:
    @dataclass
    class TaskInfo:
        task_id: str
        interval: float
        func: AsyncFunc
        args: Args = ()
        kwargs: Kwargs = field(default_factory=dict)
        run_count: int = 0
        error_count: int = 0
        last_run: datetime | None = None
        running: bool = False

    def __init__(self, logger: Logger) -> None:
        self.tasks: dict[str, AsyncScheduler.TaskInfo] = {}
        self._running: bool = False
        self._cancel_scope: anyio.CancelScope | None = None
        self._main_task: asyncio.Task[Any] | None = None
        self._thread: threading.Thread | None = None
        self._logger = logger

    def add_task(self, task_id: str, interval: float, func: AsyncFunc, args: Args = (), kwargs: Kwargs | None = None) -> None:
        """Register a new task with the scheduler."""
        if kwargs is None:
            kwargs = {}
        if task_id in self.tasks:
            raise ValueError(f"Task with id {task_id} already exists")
        self.tasks[task_id] = AsyncScheduler.TaskInfo(task_id=task_id, interval=interval, func=func, args=args, kwargs=kwargs)

    async def _run_task(self, task_id: str) -> None:
        """Internal loop for running a single task repeatedly."""
        task = self.tasks[task_id]
        while self._running:
            task.last_run = utc_now()
            task.run_count += 1
            try:
                await task.func(*task.args, **task.kwargs)
            except Exception:
                task.error_count += 1
                self._logger.exception("AsyncScheduler exception")

            # Calculate elapsed time and sleep if needed so that tasks never overlap.
            elapsed = (utc_now() - task.last_run).total_seconds()
            sleep_time = task.interval - elapsed
            if sleep_time > 0:
                try:
                    await anyio.sleep(sleep_time)
                except Exception:
                    self._logger.exception("AsyncScheduler exception")

    async def _start_all_tasks(self) -> None:
        """Starts all tasks concurrently in an AnyIO task group."""
        async with anyio.create_task_group() as tg:
            self._cancel_scope = tg.cancel_scope
            for task_id in self.tasks:
                tg.start_soon(self._run_task, task_id)
            try:
                while self._running:  # noqa: ASYNC110
                    await anyio.sleep(0.1)
            except anyio.get_cancelled_exc_class():
                self._logger.debug("Task group cancelled. Exiting _start_all_tasks.")

    def start(self) -> None:
        """
        Start the scheduler.

        This method launches the scheduler in a background thread,
        which runs an AnyIO event loop.
        """
        if self._running:
            self._logger.warning("AsyncScheduler already running")
            return
        self._running = True
        self._logger.debug("Starting AsyncScheduler")

        # Create a task in the current event loop
        self._main_task = asyncio.create_task(self._start_all_tasks())

    def stop(self) -> None:
        """
        Stop the scheduler.

        The running flag is set to False so that each task's loop will exit.
        This method then waits for the background thread to finish.
        """
        if not self._running:
            self._logger.warning("AsyncScheduler not running")
            return
        self._logger.debug("Stopping AsyncScheduler")
        self._running = False
        if self._cancel_scope is not None:
            self._cancel_scope.cancel()

        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        self._logger.debug("AsyncScheduler stopped")
