from mm_std import parse_lines, str_contains_any, str_ends_with_any, str_starts_with_any


class TestStrStartsWithAny:
    def test_starts_with_single_prefix(self):
        """Test string starting with one of the given prefixes."""
        assert str_starts_with_any("hello world", ["hello"])
        assert str_starts_with_any("test string", ["test", "other"])
        assert not str_starts_with_any("hello world", ["world"])

    def test_starts_with_multiple_prefixes(self):
        """Test string with multiple possible prefixes."""
        prefixes = ["http://", "https://", "ftp://"]
        assert str_starts_with_any("https://example.com", prefixes)
        assert str_starts_with_any("ftp://files.example.com", prefixes)
        assert not str_starts_with_any("mailto:test@example.com", prefixes)

    def test_empty_prefixes(self):
        """Test with empty prefixes list."""
        assert not str_starts_with_any("hello", [])

    def test_empty_string(self):
        """Test with empty string."""
        assert not str_starts_with_any("", ["prefix"])
        assert str_starts_with_any("", [""])

    def test_case_sensitivity(self):
        """Test that matching is case sensitive."""
        assert str_starts_with_any("Hello", ["Hello"])
        assert not str_starts_with_any("Hello", ["hello"])

    def test_accepts_different_iterables(self):
        """Test that function accepts various iterable types."""
        text = "hello world"
        assert str_starts_with_any(text, ["hello"])  # list
        assert str_starts_with_any(text, ("hello", "hi"))  # tuple
        assert str_starts_with_any(text, {"hello", "hi"})  # set
        assert str_starts_with_any(text, (p for p in ["hello", "hi"]))  # generator


class TestStrEndsWithAny:
    def test_ends_with_single_suffix(self):
        """Test string ending with one of the given suffixes."""
        assert str_ends_with_any("hello.txt", [".txt"])
        assert str_ends_with_any("document.pdf", [".pdf", ".doc"])
        assert not str_ends_with_any("hello.txt", [".pdf"])

    def test_ends_with_multiple_suffixes(self):
        """Test string with multiple possible suffixes."""
        suffixes = [".jpg", ".png", ".gif", ".bmp"]
        assert str_ends_with_any("image.png", suffixes)
        assert str_ends_with_any("photo.gif", suffixes)
        assert not str_ends_with_any("document.pdf", suffixes)

    def test_empty_suffixes(self):
        """Test with empty suffixes list."""
        assert not str_ends_with_any("hello.txt", [])

    def test_empty_string(self):
        """Test with empty string."""
        assert not str_ends_with_any("", ["suffix"])
        assert str_ends_with_any("", [""])

    def test_case_sensitivity(self):
        """Test that matching is case sensitive."""
        assert str_ends_with_any("file.TXT", [".TXT"])
        assert not str_ends_with_any("file.TXT", [".txt"])

    def test_accepts_different_iterables(self):
        """Test that function accepts various iterable types."""
        text = "file.txt"
        assert str_ends_with_any(text, [".txt"])  # list
        assert str_ends_with_any(text, (".txt", ".doc"))  # tuple
        assert str_ends_with_any(text, {".txt", ".doc"})  # set
        assert str_ends_with_any(text, (s for s in [".txt", ".doc"]))  # generator


class TestStrContainsAny:
    def test_contains_single_substring(self):
        """Test string containing one of the given substrings."""
        assert str_contains_any("hello world", ["world"])
        assert str_contains_any("the quick brown fox", ["quick", "slow"])
        assert not str_contains_any("hello world", ["foo"])

    def test_contains_multiple_substrings(self):
        """Test string with multiple possible substrings."""
        substrings = ["error", "warning", "critical"]
        assert str_contains_any("This is an error message", substrings)
        assert str_contains_any("[warning] Low disk space", substrings)
        assert not str_contains_any("Everything is fine", substrings)

    def test_empty_substrings(self):
        """Test with empty substrings list."""
        assert not str_contains_any("hello world", [])

    def test_empty_string(self):
        """Test with empty string."""
        assert not str_contains_any("", ["substring"])
        assert str_contains_any("", [""])

    def test_case_sensitivity(self):
        """Test that matching is case sensitive."""
        assert str_contains_any("Hello World", ["World"])
        assert not str_contains_any("Hello World", ["world"])

    def test_substring_overlapping(self):
        """Test with overlapping substrings."""
        text = "programming"
        assert str_contains_any(text, ["gram", "gramming"])
        assert str_contains_any(text, ["prog", "program"])

    def test_accepts_different_iterables(self):
        """Test that function accepts various iterable types."""
        text = "hello world"
        assert str_contains_any(text, ["world"])  # list
        assert str_contains_any(text, ("world", "earth"))  # tuple
        assert str_contains_any(text, {"world", "earth"})  # set
        assert str_contains_any(text, (s for s in ["world", "earth"]))  # generator


class TestParseLines:
    def test_basic_parsing(self):
        """Test basic line parsing functionality."""
        text = "line1\nline2\nline3"
        result = parse_lines(text)
        assert result == ["line1", "line2", "line3"]

    def test_empty_lines_and_whitespace(self):
        """Test handling of empty lines and whitespace."""
        text = "line1\n\n  \nline2\n   line3   \n\nline4"
        result = parse_lines(text)
        assert result == ["line1", "line2", "line3", "line4"]

    def test_lowercase_conversion(self):
        """Test lowercase parameter."""
        text = "HELLO\nWorld\nTEST"
        result = parse_lines(text, lowercase=True)
        assert result == ["hello", "world", "test"]

        # Verify original behavior without lowercase
        result_normal = parse_lines(text)
        assert result_normal == ["HELLO", "World", "TEST"]

    def test_comment_removal(self):
        """Test comment removal functionality."""
        text = "line1 # comment\nline2\nline3 # another comment\n# full comment line"
        result = parse_lines(text, remove_comments=True)
        assert result == ["line1", "line2", "line3"]

    def test_comment_removal_edge_cases(self):
        """Test comment removal with edge cases."""
        text = "line1#no space\n#comment only\n  # spaced comment  \nline2 # normal"
        result = parse_lines(text, remove_comments=True)
        assert result == ["line1", "line2"]

    def test_deduplication(self):
        """Test deduplication while preserving order."""
        text = "line1\nline2\nline1\nline3\nline2\nline4"
        result = parse_lines(text, deduplicate=True)
        assert result == ["line1", "line2", "line3", "line4"]

    def test_combined_options(self):
        """Test multiple options working together."""
        text = "HELLO # comment\nworld\nHELLO # different comment\nTEST\nworld"
        result = parse_lines(text, lowercase=True, remove_comments=True, deduplicate=True)
        assert result == ["hello", "world", "test"]

    def test_edge_cases(self):
        """Test edge cases with empty input and special characters."""
        # Empty string
        assert parse_lines("") == []

        # Only whitespace
        assert parse_lines("   \n\t\n  ") == []

        # Only comments
        assert parse_lines("# comment1\n# comment2", remove_comments=True) == []

        # Single line
        assert parse_lines("single line") == ["single line"]
