"""Tests for temperature conversion and range utilities."""

from buggy import celsius_to_fahrenheit, is_in_range, clamp


class TestCelsiusToFahrenheit:
    def test_freezing(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_boiling(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_body_temp(self):
        assert celsius_to_fahrenheit(37) == 98.6

    def test_negative(self):
        assert celsius_to_fahrenheit(-40) == -40.0


class TestIsInRange:
    def test_in_range(self):
        assert is_in_range(5, 1, 10) is True

    def test_at_lower_bound(self):
        assert is_in_range(1, 1, 10) is True

    def test_at_upper_bound(self):
        assert is_in_range(10, 1, 10) is True

    def test_below_range(self):
        assert is_in_range(0, 1, 10) is False

    def test_above_range(self):
        assert is_in_range(11, 1, 10) is False


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 1, 10) == 5

    def test_below_low(self):
        assert clamp(-5, 0, 100) == 0

    def test_above_high(self):
        assert clamp(150, 0, 100) == 100

    def test_at_low(self):
        assert clamp(0, 0, 100) == 0

    def test_at_high(self):
        assert clamp(100, 0, 100) == 100
