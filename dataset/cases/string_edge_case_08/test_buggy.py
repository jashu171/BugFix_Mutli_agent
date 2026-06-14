"""Tests for string and date utilities."""

from buggy import truncate, slugify, mask_email


class TestTruncate:
    def test_short_text(self):
        assert truncate("hello", 10) == "hello"

    def test_exact_length(self):
        assert truncate("hello", 5) == "hello"

    def test_truncated(self):
        assert truncate("hello world", 8) == "hello..."

    def test_custom_suffix(self):
        assert truncate("hello world", 7, "~") == "hello ~"

    def test_empty(self):
        assert truncate("", 5) == ""

    def test_zero_length(self):
        assert truncate("hello", 0) == ""


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_multiple_spaces(self):
        assert slugify("Hello   World") == "hello-world"

    def test_leading_trailing(self):
        assert slugify("  Hello World  ") == "hello-world"

    def test_empty(self):
        assert slugify("") == ""

    def test_special_only(self):
        assert slugify("!!!") == ""


class TestMaskEmail:
    def test_normal(self):
        assert mask_email("alice@example.com") == "a***e@example.com"

    def test_short_local(self):
        assert mask_email("ab@example.com") == "a***@example.com"

    def test_single_char(self):
        assert mask_email("a@example.com") == "a***@example.com"

    def test_long_local(self):
        assert mask_email("alexander@example.com") == "a***r@example.com"

    def test_empty(self):
        assert mask_email("") == ""

    def test_no_at(self):
        assert mask_email("invalid") == "invalid"
