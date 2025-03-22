import anyio
import pytest

from mm_std import async_synchronized, utc_now

pytestmark = pytest.mark.anyio


async def test_async_synchronized():
    @async_synchronized
    async def _task1(_p1, _p2=True):
        await anyio.sleep(1)

    @async_synchronized
    async def _task2(_p1, _p2=True):
        await anyio.sleep(1)

    start_time = utc_now()

    async with anyio.create_task_group() as tg:
        tg.start_soon(_task1, 1, False)
        tg.start_soon(_task1, 2, False)
        tg.start_soon(_task2, 1, False)
        tg.start_soon(_task2, 2, False)

    assert (utc_now() - start_time).seconds == 2
