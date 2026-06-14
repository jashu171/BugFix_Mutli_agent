"""Tests for pagination utility."""

from buggy import paginate, total_pages


class TestPaginate:
    def test_first_page(self):
        items = list(range(1, 11))
        assert paginate(items, 1, 3) == [1, 2, 3]

    def test_second_page(self):
        items = list(range(1, 11))
        assert paginate(items, 2, 3) == [4, 5, 6]

    def test_last_page_partial(self):
        items = list(range(1, 11))
        assert paginate(items, 4, 3) == [10]

    def test_beyond_last_page(self):
        items = list(range(1, 11))
        assert paginate(items, 5, 3) == []

    def test_page_size_one(self):
        items = ["a", "b", "c"]
        assert paginate(items, 2, 1) == ["b"]


class TestTotalPages:
    def test_exact_division(self):
        assert total_pages(10, 5) == 2

    def test_remainder(self):
        assert total_pages(10, 3) == 4

    def test_one_item(self):
        assert total_pages(1, 10) == 1

    def test_zero_items(self):
        assert total_pages(0, 10) == 0
