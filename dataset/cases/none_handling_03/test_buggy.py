"""Tests for user profile utilities."""

from buggy import get_display_name, format_greeting


class TestGetDisplayName:
    def test_full_name(self):
        assert get_display_name({"full_name": "Alice Smith"}) == "Alice Smith"

    def test_username_fallback(self):
        assert get_display_name({"username": "alice"}) == "alice"

    def test_email_fallback(self):
        assert get_display_name({"email": "alice@example.com"}) == "alice"

    def test_anonymous(self):
        assert get_display_name({}) == "Anonymous"

    def test_none_user(self):
        assert get_display_name(None) == "Anonymous"


class TestFormatGreeting:
    def test_morning(self):
        assert format_greeting({"full_name": "Alice"}, "morning") == "Good morning, Alice!"

    def test_none_user(self):
        assert format_greeting(None, "evening") == "Good evening, Anonymous!"
