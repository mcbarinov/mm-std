import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from typing import Any

from mm_std.date import utc_now
from mm_std.types_ import Args, AsyncFunc, Kwargs


class AsyncScheduler:
    """
    A scheduler for running async tasks at fixed intervals.

    Each task runs on its own schedule and waits for the specified interval
    between executions.
    """

    @dataclass
    class TaskInfo:
        """Information about a scheduled task."""

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
        """
        Initialize the async scheduler.

        Args:
            logger: Logger instance for recording scheduler events
        """
        self.tasks: dict[str, AsyncScheduler.TaskInfo] = {}
        self._running: bool = False
        self._tasks: list[asyncio.Task[Any]] = []
        self._main_task: asyncio.Task[Any] | None = None
        self._logger = logger

    def add_task(self, task_id: str, interval: float, func: AsyncFunc, args: Args = (), kwargs: Kwargs | None = None) -> None:
        """
        Register a new task with the scheduler.

        Args:
            task_id: Unique identifier for the task
            interval: Time in seconds between task executions
            func: Async function to execute
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function

        Raises:
            ValueError: If a task with the same ID already exists
        """
        if kwargs is None:
            kwargs = {}
        if task_id in self.tasks:
            raise ValueError(f"Task with id {task_id} already exists")
        self.tasks[task_id] = AsyncScheduler.TaskInfo(task_id=task_id, interval=interval, func=func, args=args, kwargs=kwargs)

    async def _run_task(self, task_id: str) -> None:
        """
        Internal loop for running a single task repeatedly.

        Args:
            task_id: ID of the task to run
        """
        task = self.tasks[task_id]
        task.running = True

        try:
            while self._running:
                task.last_run = utc_now()
                task.run_count += 1
                try:
                    await task.func(*task.args, **task.kwargs)
                except Exception:
                    task.error_count += 1
                    self._logger.exception(f"Exception in task {task_id}")

                # Calculate elapsed time and sleep if needed
                elapsed = (utc_now() - task.last_run).total_seconds()
                sleep_time = max(0, task.interval - elapsed)
                if sleep_time > 0:
                    try:
                        await asyncio.sleep(sleep_time)
                    except asyncio.CancelledError:
                        break
        finally:
            task.running = False
            self._logger.debug(f"Task {task_id} stopped")

    async def _start_all_tasks(self) -> None:
        """Starts all tasks concurrently using asyncio tasks."""
        self._tasks = []

        for task_id in self.tasks:
            task = asyncio.create_task(self._run_task(task_id))
            self._tasks.append(task)

        try:
            # Keep the main task alive while the scheduler is running
            while self._running:  # noqa: ASYNC110
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            self._logger.debug("Main scheduler task cancelled")
        finally:
            # Cancel all running tasks when we exit
            for task in self._tasks:
                if not task.done():
                    task.cancel()

            # Wait for all tasks to finish
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks = []

    def start(self) -> None:
        """
        Start the scheduler.

        Creates tasks in the current event loop for each registered task.
        """
        if self._running:
            self._logger.warning("AsyncScheduler already running")
            return

        self._running = True
        self._logger.debug("Starting AsyncScheduler")
        self._main_task = asyncio.create_task(self._start_all_tasks())

    def stop(self) -> None:
        """
        Stop the scheduler.

        Cancels all running tasks and waits for them to complete.
        """
        if not self._running:
            self._logger.warning("AsyncScheduler not running")
            return

        self._logger.debug("Stopping AsyncScheduler")
        self._running = False

        if self._main_task and not self._main_task.done():
            self._main_task.cancel()

        self._logger.debug("AsyncScheduler stopped")
