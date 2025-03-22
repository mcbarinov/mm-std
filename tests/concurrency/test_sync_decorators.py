import time

from mm_std import ConcurrentTasks, synchronized, synchronized_parameter, utc_now


def test_synchronized():
    @synchronized
    def _task1(_p1, _p2=True):
        time.sleep(1)
        raise RuntimeError

    @synchronized
    def _task2(_p1, _p2=True):
        time.sleep(1)
        raise RuntimeError

    start_time = utc_now()
    tasks = ConcurrentTasks()
    tasks.add_task("task1-1", _task1, args=(1, False))
    tasks.add_task("task1-2", _task1, args=(2, False))
    tasks.add_task("task2-1", _task2, args=(1, False))
    tasks.add_task("task2-2", _task2, args=(2, False))

    tasks.execute()

    assert (utc_now() - start_time).seconds == 2


def test_synchronized_parameters():
    counter = 0

    @synchronized_parameter()
    def task(_param, _second_param=None):
        nonlocal counter
        time.sleep(1)
        counter += 1

    start_time = utc_now()
    tasks = ConcurrentTasks()
    tasks.add_task("task1", task, args=(1,))
    tasks.add_task("task2", task, args=(1, 4))
    tasks.add_task("task3", task, args=(2,))
    tasks.add_task("task4", task, args=(3,))
    tasks.execute()

    assert counter == 4
    assert (utc_now() - start_time).seconds == 2


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
