"""Tests for date_utils module."""

from datetime import UTC, datetime, timedelta

import pytest

from mm_std import parse_datetime, utc_from_timestamp, utc_now, utc_now_offset


class TestUtcNow:
    """Tests for utc_now function."""

    def test_returns_datetime_with_utc_timezone(self) -> None:
        """Result has UTC timezone info."""
        result = utc_now()
        assert result.tzinfo == UTC

    def test_returns_current_time(self) -> None:
        """Result is close to actual current time."""
        before = datetime.now(UTC)
        result = utc_now()
        after = datetime.now(UTC)
        assert before <= result <= after


class TestUtcNowOffset:
    """Tests for utc_now_offset function."""

    def test_positive_days_returns_future(self) -> None:
        """Positive days parameter shifts time forward."""
        now = datetime.now(UTC)
        result = utc_now_offset(days=1)
        assert result > now
        assert result - now >= timedelta(days=1) - timedelta(seconds=1)

    def test_negative_hours_returns_past(self) -> None:
        """Negative hours parameter shifts time backward."""
        now = datetime.now(UTC)
        result = utc_now_offset(hours=-2)
        assert result < now
        assert now - result >= timedelta(hours=2) - timedelta(seconds=1)

    def test_single_param_minutes(self) -> None:
        """Works with only minutes parameter."""
        now = datetime.now(UTC)
        result = utc_now_offset(minutes=30)
        diff = result - now
        assert timedelta(minutes=29, seconds=59) <= diff <= timedelta(minutes=30, seconds=1)

    def test_single_param_seconds(self) -> None:
        """Works with only seconds parameter."""
        now = datetime.now(UTC)
        result = utc_now_offset(seconds=120)
        diff = result - now
        assert timedelta(seconds=119) <= diff <= timedelta(seconds=121)

    def test_combined_params(self) -> None:
        """Works with multiple parameters combined."""
        now = datetime.now(UTC)
        result = utc_now_offset(days=1, hours=2, minutes=30, seconds=15)
        expected_delta = timedelta(days=1, hours=2, minutes=30, seconds=15)
        diff = result - now
        assert expected_delta - timedelta(seconds=1) <= diff <= expected_delta + timedelta(seconds=1)

    def test_no_params_returns_current_time(self) -> None:
        """Returns current time when called without parameters."""
        before = datetime.now(UTC)
        result = utc_now_offset()
        after = datetime.now(UTC)
        assert before <= result <= after


class TestUtcFromTimestamp:
    """Tests for utc_from_timestamp function."""

    def test_known_timestamp(self) -> None:
        """Converts known Unix timestamp correctly."""
        # 2023-12-25 00:00:00 UTC
        timestamp = 1703462400.0
        result = utc_from_timestamp(timestamp)
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0

    def test_result_has_utc_timezone(self) -> None:
        """Result has UTC timezone info."""
        result = utc_from_timestamp(0)
        assert result.tzinfo == UTC

    def test_epoch(self) -> None:
        """Unix epoch converts to 1970-01-01 00:00:00 UTC."""
        result = utc_from_timestamp(0)
        assert result == datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)


class TestParseDatetime:
    """Tests for parse_datetime function."""

    @pytest.mark.parametrize(
        (
            "date_str",
            "expected_year",
            "expected_month",
            "expected_day",
            "expected_hour",
            "expected_minute",
            "expected_second",
            "expected_microsecond",
        ),
        [
            ("2023-12-25", 2023, 12, 25, 0, 0, 0, 0),
            ("2023/12/25", 2023, 12, 25, 0, 0, 0, 0),
            ("2023-12-25 10:30", 2023, 12, 25, 10, 30, 0, 0),
            ("2023-12-25 10:30:45", 2023, 12, 25, 10, 30, 45, 0),
            ("2023-12-25T10:30:00Z", 2023, 12, 25, 10, 30, 0, 0),
            ("2023-12-25T10:30:00+00:00", 2023, 12, 25, 10, 30, 0, 0),
            ("2023-12-25 10:30:00.123456", 2023, 12, 25, 10, 30, 0, 123456),
            ("2023-12-25 10:30:00.123456+00:00", 2023, 12, 25, 10, 30, 0, 123456),
        ],
    )
    def test_parses_various_formats(
        self,
        date_str: str,
        expected_year: int,
        expected_month: int,
        expected_day: int,
        expected_hour: int,
        expected_minute: int,
        expected_second: int,
        expected_microsecond: int,
    ) -> None:
        """Parses date strings in various formats."""
        result = parse_datetime(date_str)
        assert result.year == expected_year
        assert result.month == expected_month
        assert result.day == expected_day
        assert result.hour == expected_hour
        assert result.minute == expected_minute
        assert result.second == expected_second
        assert result.microsecond == expected_microsecond

    def test_z_suffix_parsed_as_utc(self) -> None:
        """Z suffix is converted to UTC timezone."""
        result = parse_datetime("2023-12-25T10:30:00Z")
        assert result.tzinfo is not None

    def test_ignore_tz_strips_timezone(self) -> None:
        """ignore_tz=True removes timezone info."""
        result = parse_datetime("2023-12-25T10:30:00+02:00", ignore_tz=True)
        assert result.tzinfo is None
        assert result.hour == 10  # hour is preserved, not converted

    def test_invalid_format_raises_value_error(self) -> None:
        """Unknown format raises ValueError."""
        with pytest.raises(ValueError, match="does not match any known format"):
            parse_datetime("not-a-date")

    def test_lowercase_z_suffix(self) -> None:
        """Lowercase 'z' suffix is also handled."""
        result = parse_datetime("2023-12-25T10:30:00z")
        assert result.year == 2023
        assert result.tzinfo is not None
