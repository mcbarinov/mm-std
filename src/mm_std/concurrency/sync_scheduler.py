import time
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from threading import Thread

from mm_std.date import is_too_old, utc_now
from mm_std.types_ import Func


class Scheduler:
    def __init__(self, log: Logger, loop_delay: float = 0.5, debug: bool = False) -> None:
        self.log = log
        self.debug = debug
        self.loop_delay = loop_delay
        self.stopped = False
        self.jobs: list[Scheduler.Job] = []
        self.run_immediately_jobs: list[Scheduler.Job] = []
        self._debug("init")

    @dataclass
    class Job:
        func: Func
        args: tuple[object, ...]
        interval: int
        is_running: bool = False
        last_at: datetime = field(default_factory=utc_now)

        def __str__(self) -> str:
            return str(self.func)

    def add_job(self, func: Func, interval: int, args: tuple[object, ...] = (), run_immediately: bool = False) -> None:
        job = Scheduler.Job(func, args, interval)
        self.jobs.append(job)
        if run_immediately:
            self.run_immediately_jobs.append(job)

    def _run_job(self, job: Job) -> None:
        self._debug(f"_run_job: {job}")
        if self.stopped:
            return
        try:
            job.func(*job.args)
            self._debug(f"_run_job: {job} done")
        except Exception:
            self.log.exception("scheduler error")
            self._debug(f"_run_job: {job} error")
        finally:
            job.is_running = False

    def _start(self) -> None:
        self._debug(f"_start: jobs={len(self.jobs)}, run_immediately_jobs={len(self.run_immediately_jobs)}")
        for j in self.run_immediately_jobs:
            j.is_running = True
            j.last_at = utc_now()
            Thread(target=self._run_job, args=(j,)).start()
        while not self.stopped:
            for j in self.jobs:
                if not j.is_running and is_too_old(j.last_at, j.interval):
                    j.is_running = True
                    j.last_at = utc_now()
                    Thread(target=self._run_job, args=(j,)).start()
            time.sleep(self.loop_delay)

    def _debug(self, message: str) -> None:
        if self.debug:
            self.log.debug("Scheduler: %s", message)

    def start(self) -> None:
        Thread(target=self._start).start()

    def stop(self) -> None:
        self.stopped = True
