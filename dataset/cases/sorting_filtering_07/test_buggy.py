"""Tests for product catalog utilities."""

from buggy import sort_by_price, filter_in_stock, top_n_expensive

PRODUCTS = [
    {"name": "Widget", "price": 10, "quantity": 5},
    {"name": "Gadget", "price": 50, "quantity": 0},
    {"name": "Doohickey", "price": 30, "quantity": 2},
    {"name": "Thingamajig", "price": 20, "quantity": 10},
]


class TestSortByPrice:
    def test_ascending(self):
        result = sort_by_price(PRODUCTS)
        names = [p["name"] for p in result]
        assert names == ["Widget", "Thingamajig", "Doohickey", "Gadget"]

    def test_descending(self):
        result = sort_by_price(PRODUCTS, descending=True)
        names = [p["name"] for p in result]
        assert names == ["Gadget", "Doohickey", "Thingamajig", "Widget"]

    def test_does_not_mutate(self):
        original = list(PRODUCTS)
        sort_by_price(PRODUCTS)
        assert PRODUCTS == original


class TestFilterInStock:
    def test_filters_zero_quantity(self):
        result = filter_in_stock(PRODUCTS)
        names = [p["name"] for p in result]
        assert "Gadget" not in names

    def test_keeps_in_stock(self):
        result = filter_in_stock(PRODUCTS)
        assert len(result) == 3

    def test_all_out_of_stock(self):
        products = [{"name": "A", "quantity": 0}, {"name": "B", "quantity": 0}]
        assert filter_in_stock(products) == []


class TestTopNExpensive:
    def test_top_2(self):
        result = top_n_expensive(PRODUCTS, 2)
        names = [p["name"] for p in result]
        assert names == ["Gadget", "Doohickey"]

    def test_top_1(self):
        result = top_n_expensive(PRODUCTS, 1)
        assert result[0]["name"] == "Gadget"

    def test_n_larger_than_list(self):
        result = top_n_expensive(PRODUCTS, 10)
        assert len(result) == 4
