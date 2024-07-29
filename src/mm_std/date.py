import random
from datetime import UTC, datetime, timedelta

from dateutil import parser


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_delta(
    *,
    days: int | None = None,
    hours: int | None = None,
    minutes: int | None = None,
    seconds: int | None = None,
) -> datetime:
    params = {}
    if days:
        params["days"] = days
    if hours:
        params["hours"] = hours
    if minutes:
        params["minutes"] = minutes
    if seconds:
        params["seconds"] = seconds
    return datetime.now(UTC) + timedelta(**params)


def parse_date(value: str, ignore_tz: bool = False) -> datetime:
    return parser.parse(value, ignoretz=ignore_tz)


def utc_random(
    *,
    from_time: datetime | None = None,
    range_hours: int = 0,
    range_minutes: int = 0,
    range_seconds: int = 0,
) -> datetime:
    if from_time is None:
        from_time = utc_now()
    to_time = from_time + timedelta(hours=range_hours, minutes=range_minutes, seconds=range_seconds)
    return from_time + (to_time - from_time) * random.random()


def is_too_old(value: datetime | None, seconds: int) -> bool:
    return value is None or value < utc_delta(seconds=-1 * seconds)
