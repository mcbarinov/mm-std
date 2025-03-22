import anyio
import pytest

from mm_std import AsyncTaskRunner

pytestmark = pytest.mark.anyio


async def test_basic_execution():
    runner = AsyncTaskRunner(max_concurrent_tasks=2)

    async def example_task(value):
        await anyio.sleep(0.1)
        return value * 2

    runner.add_task("task1", example_task, 5)
    runner.add_task("task2", example_task, 10)

    result = await runner.run()

    assert result.is_ok is True
    assert result.is_timeout is False
    assert result.results == {"task1": 10, "task2": 20}
    assert result.exceptions == {}


async def test_exception_handling():
    runner = AsyncTaskRunner(max_concurrent_tasks=2)

    async def successful_task():
        return "success"

    async def failing_task():
        raise ValueError("Expected error")

    runner.add_task("success", successful_task)
    runner.add_task("fail", failing_task)

    result = await runner.run()

    assert result.is_ok is False
    assert result.results == {"success": "success"}
    assert "fail" in result.exceptions
    assert isinstance(result.exceptions["fail"], ValueError)


async def test_concurrency_limit():
    max_concurrency = 2
    runner = AsyncTaskRunner(max_concurrent_tasks=max_concurrency)
    running_tasks = 0
    max_observed_concurrency = 0

    async def concurrent_task(task_num):
        nonlocal running_tasks, max_observed_concurrency
        running_tasks += 1
        max_observed_concurrency = max(max_observed_concurrency, running_tasks)
        await anyio.sleep(0.2)  # Long enough to ensure overlap
        running_tasks -= 1
        return task_num

    for i in range(5):
        runner.add_task(f"task{i}", concurrent_task, i)

    result = await runner.run()

    assert result.is_ok is True
    assert max_observed_concurrency <= max_concurrency
    assert len(result.results) == 5


async def test_timeout():
    runner = AsyncTaskRunner(max_concurrent_tasks=2, timeout=0.3)

    async def slow_task():
        await anyio.sleep(1.0)
        return "completed"

    runner.add_task("slow1", slow_task)
    runner.add_task("slow2", slow_task)

    result = await runner.run()

    assert result.is_timeout is True
    assert result.is_ok is False


async def test_runner_reuse():
    runner = AsyncTaskRunner(max_concurrent_tasks=2)

    async def simple_task():
        return "done"

    runner.add_task("task1", simple_task)
    await runner.run()

    with pytest.raises(RuntimeError):
        await runner.run()

    with pytest.raises(RuntimeError):
        runner.add_task("task2", simple_task)


async def test_task_id_validation():
    runner = AsyncTaskRunner(max_concurrent_tasks=2)

    async def simple_task():
        return "done"

    with pytest.raises(ValueError):
        runner.add_task("", simple_task)

    runner.add_task("task1", simple_task)

    with pytest.raises(ValueError):
        runner.add_task("task1", simple_task)


def test_invalid_timeout():
    with pytest.raises(ValueError):
        AsyncTaskRunner(max_concurrent_tasks=2, timeout=-1)
