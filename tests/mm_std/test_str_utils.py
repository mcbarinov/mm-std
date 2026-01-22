"""Tests for str_utils module."""

import pytest

from mm_std import parse_lines, str_contains_any, str_ends_with_any, str_starts_with_any


class TestStrStartsWithAny:
    """Tests for str_starts_with_any function."""

    @pytest.mark.parametrize(
        ("value", "prefixes", "expected"),
        [
            ("hello world", ["hello", "hi", "hey"], True),  # match first
            ("hello world", ["hi", "hello", "hey"], True),  # match middle
            ("hello world", ["hi", "hey", "hello"], True),  # match last
            ("https://example.com", ["http://", "https://"], True),
            ("admin_user", ("admin_", "super_", "root_"), True),  # tuple
        ],
    )
    def test_match_found(self, value: str, prefixes: list[str] | tuple[str, ...], expected: bool) -> None:
        """Returns True when string starts with any prefix."""
        assert str_starts_with_any(value, prefixes) == expected

    @pytest.mark.parametrize(
        ("value", "prefixes"),
        [
            ("hello world", ["bye", "hi", "hey"]),
            ("user_admin", ["admin_", "super_"]),
            ("ftp://example.com", ["http://", "https://"]),
        ],
    )
    def test_no_match(self, value: str, prefixes: list[str]) -> None:
        """Returns False when string doesn't start with any prefix."""
        assert str_starts_with_any(value, prefixes) is False

    def test_empty_prefixes(self) -> None:
        """Returns False when prefixes iterable is empty."""
        assert str_starts_with_any("hello", []) is False

    def test_empty_string_value(self) -> None:
        """Empty string doesn't match non-empty prefixes."""
        assert str_starts_with_any("", ["hello", "world"]) is False

    def test_empty_string_matches_empty_prefix(self) -> None:
        """Empty string matches empty prefix."""
        assert str_starts_with_any("", [""]) is True
        assert str_starts_with_any("hello", [""]) is True

    def test_generator_iterable(self) -> None:
        """Accepts generator as iterable."""
        prefixes = (p for p in ["hello", "hi"])
        assert str_starts_with_any("hello world", prefixes) is True


class TestStrEndsWithAny:
    """Tests for str_ends_with_any function."""

    @pytest.mark.parametrize(
        ("value", "suffixes", "expected"),
        [
            ("document.pdf", [".pdf", ".doc", ".docx"], True),  # match first
            ("document.pdf", [".doc", ".pdf", ".docx"], True),  # match middle
            ("document.pdf", [".doc", ".docx", ".pdf"], True),  # match last
            ("image.PNG", [".png", ".jpg", ".PNG"], True),
            ("config.yaml", (".yml", ".yaml", ".json"), True),  # tuple
        ],
    )
    def test_match_found(self, value: str, suffixes: list[str] | tuple[str, ...], expected: bool) -> None:
        """Returns True when string ends with any suffix."""
        assert str_ends_with_any(value, suffixes) == expected

    @pytest.mark.parametrize(
        ("value", "suffixes"),
        [
            ("document.txt", [".pdf", ".doc", ".docx"]),
            ("image.gif", [".png", ".jpg", ".jpeg"]),
            ("no_extension", [".txt", ".md"]),
        ],
    )
    def test_no_match(self, value: str, suffixes: list[str]) -> None:
        """Returns False when string doesn't end with any suffix."""
        assert str_ends_with_any(value, suffixes) is False

    def test_empty_suffixes(self) -> None:
        """Returns False when suffixes iterable is empty."""
        assert str_ends_with_any("hello.txt", []) is False

    def test_empty_string_value(self) -> None:
        """Empty string doesn't match non-empty suffixes."""
        assert str_ends_with_any("", [".txt", ".md"]) is False

    def test_empty_string_matches_empty_suffix(self) -> None:
        """Empty string matches empty suffix."""
        assert str_ends_with_any("", [""]) is True
        assert str_ends_with_any("hello", [""]) is True

    def test_generator_iterable(self) -> None:
        """Accepts generator as iterable."""
        suffixes = (s for s in [".pdf", ".txt"])
        assert str_ends_with_any("document.pdf", suffixes) is True


class TestStrContainsAny:
    """Tests for str_contains_any function."""

    @pytest.mark.parametrize(
        ("value", "substrings", "expected"),
        [
            ("hello world", ["hello", "foo", "bar"], True),  # at start
            ("hello world", ["foo", "wor", "bar"], True),  # in middle
            ("hello world", ["foo", "bar", "world"], True),  # at end
            ("ERROR: connection failed", ["ERROR", "WARN", "INFO"], True),
            ("the quick brown fox", ("quick", "slow"), True),  # tuple
        ],
    )
    def test_match_found(self, value: str, substrings: list[str] | tuple[str, ...], expected: bool) -> None:
        """Returns True when string contains any substring."""
        assert str_contains_any(value, substrings) == expected

    @pytest.mark.parametrize(
        ("value", "substrings"),
        [
            ("hello world", ["foo", "bar", "baz"]),
            ("INFO: all good", ["ERROR", "WARN", "CRITICAL"]),
            ("abc", ["abcd", "bcd", "cde"]),
        ],
    )
    def test_no_match(self, value: str, substrings: list[str]) -> None:
        """Returns False when string doesn't contain any substring."""
        assert str_contains_any(value, substrings) is False

    def test_empty_substrings(self) -> None:
        """Returns False when substrings iterable is empty."""
        assert str_contains_any("hello", []) is False

    def test_empty_string_value(self) -> None:
        """Empty string doesn't contain non-empty substrings."""
        assert str_contains_any("", ["hello", "world"]) is False

    def test_empty_string_matches_empty_substring(self) -> None:
        """Empty substring is contained in any string."""
        assert str_contains_any("", [""]) is True
        assert str_contains_any("hello", [""]) is True

    def test_generator_iterable(self) -> None:
        """Accepts generator as iterable."""
        substrings = (s for s in ["error", "warning"])
        assert str_contains_any("error occurred", substrings) is True


class TestParseLines:
    """Tests for parse_lines function - basic functionality."""

    def test_basic_parsing(self) -> None:
        """Strips whitespace and removes empty lines."""
        text = "  line1  \n  line2  \n\n  line3  "
        result = parse_lines(text)
        assert result == ["line1", "line2", "line3"]

    def test_removes_empty_lines(self) -> None:
        """Empty lines are filtered out."""
        text = "line1\n\n\nline2\n   \nline3"
        result = parse_lines(text)
        assert result == ["line1", "line2", "line3"]

    def test_empty_input(self) -> None:
        """Empty string returns empty list."""
        assert parse_lines("") == []

    def test_only_whitespace(self) -> None:
        """Whitespace-only input returns empty list."""
        assert parse_lines("   \n   \n   ") == []

    def test_single_line(self) -> None:
        """Single line is parsed correctly."""
        assert parse_lines("  hello  ") == ["hello"]


class TestParseLinesLowercase:
    """Tests for parse_lines with lowercase option."""

    def test_lowercase_enabled(self) -> None:
        """Lines are converted to lowercase when enabled."""
        text = "HELLO\nWorld\nmixed CASE"
        result = parse_lines(text, lowercase=True)
        assert result == ["hello", "world", "mixed case"]

    def test_lowercase_disabled_by_default(self) -> None:
        """Case is preserved by default."""
        text = "HELLO\nWorld"
        result = parse_lines(text)
        assert result == ["HELLO", "World"]


class TestParseLinesRemoveComments:
    """Tests for parse_lines with remove_comments option."""

    def test_removes_inline_comments(self) -> None:
        """Content after # is removed."""
        text = "value1 # comment\nvalue2#no space\nvalue3"
        result = parse_lines(text, remove_comments=True)
        assert result == ["value1", "value2", "value3"]

    def test_removes_comment_only_lines(self) -> None:
        """Lines that become empty after comment removal are filtered."""
        text = "value1\n# full comment\nvalue2\n   # indented comment"
        result = parse_lines(text, remove_comments=True)
        assert result == ["value1", "value2"]

    def test_preserves_comments_by_default(self) -> None:
        """Comments are preserved when option is disabled."""
        text = "value # comment"
        result = parse_lines(text)
        assert result == ["value # comment"]


class TestParseLinesDeduplicate:
    """Tests for parse_lines with deduplicate option."""

    def test_removes_duplicates(self) -> None:
        """Duplicate lines are removed."""
        text = "line1\nline2\nline1\nline3\nline2"
        result = parse_lines(text, deduplicate=True)
        assert result == ["line1", "line2", "line3"]

    def test_preserves_order(self) -> None:
        """First occurrence order is preserved."""
        text = "c\na\nb\na\nc"
        result = parse_lines(text, deduplicate=True)
        assert result == ["c", "a", "b"]

    def test_allows_duplicates_by_default(self) -> None:
        """Duplicates are kept when option is disabled."""
        text = "line1\nline1\nline1"
        result = parse_lines(text)
        assert result == ["line1", "line1", "line1"]


class TestParseLinesCombined:
    """Tests for parse_lines with combined options."""

    def test_all_options_enabled(self) -> None:
        """All options work together correctly."""
        text = """
        DEBUG=true # Enable debug
        HOST=localhost
        PORT=8080 # Port config
        # Comment line
        DEBUG=true # Duplicate
        """
        result = parse_lines(text, lowercase=True, remove_comments=True, deduplicate=True)
        assert result == ["debug=true", "host=localhost", "port=8080"]

    def test_lowercase_before_deduplicate(self) -> None:
        """Lowercase is applied before deduplication."""
        text = "HELLO\nhello\nHELLO"
        result = parse_lines(text, lowercase=True, deduplicate=True)
        assert result == ["hello"]

    def test_comments_removed_before_deduplicate(self) -> None:
        """Comments are removed before deduplication."""
        text = "value # comment1\nvalue # comment2"
        result = parse_lines(text, remove_comments=True, deduplicate=True)
        assert result == ["value"]
