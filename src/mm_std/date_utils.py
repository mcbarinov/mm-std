"""UTC-focused datetime operations and flexible date parsing."""

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(UTC)


def utc_now_offset(
    *, days: int | None = None, hours: int | None = None, minutes: int | None = None, seconds: int | None = None
) -> datetime:
    """Get UTC time shifted by the specified delta.

    Use negative values to get time in the past.
    """
    params = {}
    if days is not None:
        params["days"] = days
    if hours is not None:
        params["hours"] = hours
    if minutes is not None:
        params["minutes"] = minutes
    if seconds is not None:
        params["seconds"] = seconds
    return datetime.now(UTC) + timedelta(**params)


def utc_from_timestamp(timestamp: float) -> datetime:
    """Create UTC datetime from Unix timestamp."""
    return datetime.fromtimestamp(timestamp, UTC)


def parse_datetime(date_str: str, ignore_tz: bool = False) -> datetime:
    """Parse date string in various formats, with timezone handling.

    Converts 'Z' suffix to '+00:00' for ISO format compatibility.
    Use ignore_tz=True to strip timezone info from the result.
    """
    if date_str.lower().endswith("z"):
        date_str = date_str[:-1] + "+00:00"
    date_formats = [
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M%z",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        # Add more formats as needed
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)  # noqa: DTZ007 - timezone deliberately ignored when ignore_tz=True
            if ignore_tz and dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt  # noqa: TRY300 - return in try block is intentional for parse flow
        except ValueError:
            continue
    raise ValueError(f"Time data '{date_str}' does not match any known format.")
