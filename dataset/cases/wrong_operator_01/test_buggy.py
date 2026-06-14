"""Tests for discount calculations."""

from buggy import apply_discount, bulk_discount
import pytest


class TestApplyDiscount:
    def test_basic_discount(self):
        assert apply_discount(100, 10) == 90.0

    def test_zero_discount(self):
        assert apply_discount(100, 0) == 100.0

    def test_full_discount(self):
        assert apply_discount(100, 100) == 0.0

    def test_half_discount(self):
        assert apply_discount(200, 50) == 100.0

    def test_small_discount(self):
        assert apply_discount(49.99, 15) == 42.49

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            apply_discount(-10, 10)

    def test_invalid_discount_raises(self):
        with pytest.raises(ValueError):
            apply_discount(100, 110)


class TestBulkDiscount:
    def test_above_threshold(self):
        prices = [100, 200, 300]
        result = bulk_discount(prices, 3, 10)
        assert result == [90.0, 180.0, 270.0]

    def test_below_threshold(self):
        prices = [100, 200]
        result = bulk_discount(prices, 3, 10)
        assert result == prices
