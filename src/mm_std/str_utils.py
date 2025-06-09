from collections.abc import Iterable


def str_starts_with_any(value: str, prefixes: Iterable[str]) -> bool:
    """Check if string starts with any of the given prefixes."""
    return any(value.startswith(prefix) for prefix in prefixes)


def str_ends_with_any(value: str, suffixes: Iterable[str]) -> bool:
    """Check if string ends with any of the given suffixes."""
    return any(value.endswith(suffix) for suffix in suffixes)


def str_contains_any(value: str, substrings: Iterable[str]) -> bool:
    """Check if string contains any of the given substrings."""
    return any(substring in value for substring in substrings)
