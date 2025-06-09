from mm_std import str_contains_any, str_ends_with_any, str_starts_with_any


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
