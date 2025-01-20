from datetime import UTC, datetime, timedelta

from mm_std.date import parse_date, utc_delta


def test_utc_delta():
    now = datetime.now(UTC)
    d1 = now - timedelta(hours=13, minutes=13, seconds=13)
    res = utc_delta(hours=-13, minutes=-13, seconds=-13)

    assert abs(d1 - res) < timedelta(seconds=1)

    now = datetime.now(UTC)
    d1 = now + timedelta(hours=13, minutes=13, seconds=13)
    res = utc_delta(hours=13, minutes=13, seconds=13)

    assert abs(d1 - res) < timedelta(seconds=1)


def test_parse_date():
    res = parse_date("2018-01-06 22:36:00")
    assert res == datetime(2018, 1, 6, 22, 36, tzinfo=None)  # noqa: DTZ001

    res = parse_date("2024-11-18T08:44:28.975000+00:00")
    assert res == datetime(2024, 11, 18, 8, 44, 28, 975000, tzinfo=UTC)

    res = parse_date("2024-11-18T08:44:28.975000Z")
    assert res == datetime(2024, 11, 18, 8, 44, 28, 975000, tzinfo=UTC)
