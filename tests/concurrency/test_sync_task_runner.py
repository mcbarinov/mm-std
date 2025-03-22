import time

from mm_std import ConcurrentTasks


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
