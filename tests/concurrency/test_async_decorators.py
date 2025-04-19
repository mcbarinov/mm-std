import asyncio

from mm_std import async_synchronized, async_synchronized_parameter, utc_now


async def test_async_synchronized():
    @async_synchronized
    async def _task1(_p1, _p2=True):
        await asyncio.sleep(1)

    @async_synchronized
    async def _task2(_p1, _p2=True):
        await asyncio.sleep(1)

    start_time = utc_now()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(_task1(1, False))
        tg.create_task(_task1(2, False))
        tg.create_task(_task2(1, False))
        tg.create_task(_task2(2, False))

    assert (utc_now() - start_time).seconds == 2


async def test_async_synchronized_parameters():
    counter = 0

    @async_synchronized_parameter()
    async def task(_param, _second_param=None):
        nonlocal counter
        await asyncio.sleep(1)
        counter += 1

    start_time = utc_now()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(task(1))
        tg.create_task(task(1, 4))
        tg.create_task(task(2))
        tg.create_task(task(3))

    assert counter == 4
    assert (utc_now() - start_time).seconds == 2


async def test_async_synchronized_parameters_skip_if_locked():
    counter = 0

    @async_synchronized_parameter(skip_if_locked=True)
    async def task(_param, _second_param=None):
        nonlocal counter
        await asyncio.sleep(1)
        counter += 1

    async with asyncio.TaskGroup() as tg:
        tg.create_task(task(1))
        tg.create_task(task(1, 4))
        tg.create_task(task(2))
        tg.create_task(task(3))

    assert counter == 3
