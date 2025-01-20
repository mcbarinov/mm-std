import logging
import time
from datetime import UTC, datetime

from mm_std import ConcurrentTasks
from mm_std.concurrency import Scheduler, synchronized, synchronized_parameter


def task1() -> str:
    time.sleep(1)
    return "r1"


def task2(name: str, value: str) -> str:
    time.sleep(1)
    return f"r2/{name}/{value}"


def task3(*, p1: str, p2: str) -> str:
    time.sleep(1)
    return f"r3/{p1}/{p2}"


def task4():
    raise RuntimeError("moo")


def task5(seconds: int):
    time.sleep(seconds)


def task6():
    pass


def test_ok():
    tasks = ConcurrentTasks()
    tasks.add_task("task1", task1)
    tasks.add_task("task2", task2, ("aaa", "bbb"))
    tasks.add_task("task3", task3, kwargs={"p1": "aaa", "p2": "bbb"})
    tasks.execute()

    assert not tasks.error
    assert not tasks.timeout_error
    assert tasks.exceptions == {}
    assert tasks.result == {"task1": "r1", "task2": "r2/aaa/bbb", "task3": "r3/aaa/bbb"}


def test_exceptions():
    tasks = ConcurrentTasks()
    tasks.add_task("task1", task1)
    tasks.add_task("task4", task4)
    tasks.execute()

    assert tasks.error
    assert not tasks.timeout_error
    assert len(tasks.exceptions) == 1
    assert tasks.result == {"task1": "r1"}


def test_timeout():
    tasks = ConcurrentTasks(timeout=3)
    tasks.add_task("task1", task1)
    tasks.add_task("task5", task5, (5,))
    tasks.execute()

    assert tasks.error
    assert tasks.timeout_error
    assert tasks.result == {"task1": "r1"}


def test_synchronized():
    @synchronized
    def _task1(_p1, _p2=True):
        time.sleep(1)
        raise RuntimeError

    @synchronized
    def _task2(_p1, _p2=True):
        time.sleep(1)
        raise RuntimeError

    start_time = datetime.now(tz=UTC)
    tasks = ConcurrentTasks()
    tasks.add_task("task1-1", _task1, args=(1, False))
    tasks.add_task("task1-2", _task1, args=(2, False))
    tasks.add_task("task2-1", _task2, args=(1, False))
    tasks.add_task("task2-2", _task2, args=(2, False))

    tasks.execute()
    end_time = datetime.now(tz=UTC)

    assert (end_time - start_time).seconds == 2


def test_synchronized_parameters():
    counter = 0

    @synchronized_parameter()
    def task(_param, _second_param=None):
        nonlocal counter
        time.sleep(1)
        counter += 1

    start_time = datetime.now(tz=UTC)
    tasks = ConcurrentTasks()
    tasks.add_task("task1", task, args=(1,))
    tasks.add_task("task2", task, args=(1, 4))
    tasks.add_task("task3", task, args=(2,))
    tasks.add_task("task4", task, args=(3,))
    tasks.execute()
    end_time = datetime.now(tz=UTC)

    assert counter == 4
    assert (end_time - start_time).seconds == 2


def test_synchronized_parameters_skip_if_locked():
    counter = 0

    @synchronized_parameter(skip_if_locked=True)
    def task(_param, _second_param=None):
        nonlocal counter
        time.sleep(1)
        counter += 1

    tasks = ConcurrentTasks()
    tasks.add_task("task1", task, args=(1,))
    tasks.add_task("task2", task, args=(1, 4))
    tasks.add_task("task3", task, args=(2,))
    tasks.add_task("task4", task, args=(3,))
    tasks.execute()

    assert counter == 3


def test_scheduler():
    logger = logging.getLogger()
    scheduler = Scheduler(logger)
    scheduler.add_job(lambda x: x, 5)
    scheduler.start()
    scheduler.stop()
