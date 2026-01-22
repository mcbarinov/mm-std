"""Tests for random_utils module."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from mm_std import random_datetime, random_datetime_offset, random_decimal


class TestRandomDecimal:
    """Tests for random_decimal function."""

    def test_result_within_bounds(self) -> None:
        """Result is between from_value and to_value."""
        from_val = Decimal("10.00")
        to_val = Decimal("20.00")
        for _ in range(100):
            result = random_decimal(from_val, to_val)
            assert from_val <= result <= to_val

    def test_precision_preserved(self) -> None:
        """Decimal precision is maintained."""
        from_val = Decimal("1.23")
        to_val = Decimal("1.45")
        for _ in range(100):
            result = random_decimal(from_val, to_val)
            # Result should have at most 2 decimal places
            assert result == result.quantize(Decimal("0.01"))

    def test_equal_values_returns_same(self) -> None:
        """When from == to, returns that value."""
        value = Decimal("42.50")
        result = random_decimal(value, value)
        assert result == value

    def test_invalid_range_raises_value_error(self) -> None:
        """Raises ValueError when from > to."""
        with pytest.raises(ValueError, match="from_value must be <= to_value"):
            random_decimal(Decimal("20.00"), Decimal("10.00"))


class TestRandomDatetime:
    """Tests for random_datetime function."""

    def test_result_within_bounds(self) -> None:
        """Result is between from_time and to_time."""
        from_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)
        to_time = datetime(2023, 12, 31, 23, 59, 59, tzinfo=UTC)
        for _ in range(100):
            result = random_datetime(from_time, to_time)
            assert from_time <= result <= to_time

    def test_equal_times_returns_same(self) -> None:
        """When from == to, returns that value."""
        value = datetime(2023, 6, 15, 12, 30, 0, tzinfo=UTC)
        result = random_datetime(value, value)
        assert result == value

    def test_invalid_range_raises_value_error(self) -> None:
        """Raises ValueError when from > to."""
        from_time = datetime(2023, 12, 31, tzinfo=UTC)
        to_time = datetime(2023, 1, 1, tzinfo=UTC)
        with pytest.raises(ValueError, match="from_time must be <= to_time"):
            random_datetime(from_time, to_time)

    def test_preserves_timezone(self) -> None:
        """Timezone info is preserved from input."""
        tz = timezone(timedelta(hours=5))
        from_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=tz)
        to_time = datetime(2023, 1, 2, 0, 0, 0, tzinfo=tz)
        result = random_datetime(from_time, to_time)
        assert result.tzinfo == tz


class TestRandomDatetimeOffset:
    """Tests for random_datetime_offset function."""

    def test_hours_only(self) -> None:
        """Works with only hours param."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        for _ in range(100):
            result = random_datetime_offset(base, hours=2)
            assert base <= result <= base + timedelta(hours=2)

    def test_minutes_only(self) -> None:
        """Works with only minutes param."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        for _ in range(100):
            result = random_datetime_offset(base, minutes=30)
            assert base <= result <= base + timedelta(minutes=30)

    def test_seconds_only(self) -> None:
        """Works with only seconds param."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        for _ in range(100):
            result = random_datetime_offset(base, seconds=45)
            assert base <= result <= base + timedelta(seconds=45)

    def test_combined_params(self) -> None:
        """Works with all params combined."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        expected_max = base + timedelta(hours=1, minutes=30, seconds=45)
        for _ in range(100):
            result = random_datetime_offset(base, hours=1, minutes=30, seconds=45)
            assert base <= result <= expected_max

    def test_zero_offset_returns_base(self) -> None:
        """No offset returns from_time."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        result = random_datetime_offset(base)
        assert result == base

    @pytest.mark.parametrize(
        ("hours", "minutes", "seconds"),
        [
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, -1),
        ],
    )
    def test_negative_value_raises_value_error(self, hours: int, minutes: int, seconds: int) -> None:
        """Negative values raise ValueError."""
        base = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        with pytest.raises(ValueError, match="Offset values must be non-negative"):
            random_datetime_offset(base, hours=hours, minutes=minutes, seconds=seconds)
