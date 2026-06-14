"""Tests for statistics utilities."""

from buggy import safe_average, safe_max, running_total


class TestSafeAverage:
    def test_normal(self):
        assert safe_average([1, 2, 3]) == 2.0

    def test_single(self):
        assert safe_average([5]) == 5.0

    def test_empty(self):
        assert safe_average([]) is None


class TestSafeMax:
    def test_normal(self):
        assert safe_max([1, 3, 2]) == 3

    def test_single(self):
        assert safe_max([7]) == 7

    def test_empty_default(self):
        assert safe_max([], default=0) == 0

    def test_empty_none(self):
        assert safe_max([]) is None


class TestRunningTotal:
    def test_normal(self):
        assert running_total([1, 2, 3]) == [1, 3, 6]

    def test_single(self):
        assert running_total([5]) == [5]

    def test_empty(self):
        assert running_total([]) == []
