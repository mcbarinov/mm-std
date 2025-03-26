import asyncio

import pytest

from mm_std import async_synchronized, utc_now

pytestmark = pytest.mark.asyncio


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
