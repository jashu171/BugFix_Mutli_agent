"""Product catalog utilities."""

from typing import Optional


def sort_by_price(products: list[dict], descending: bool = False) -> list[dict]:
    """Sort products by price.

    Args:
        products: List of dicts with at least a 'price' key.
        descending: If True, sort highest-first.

    Returns:
        New sorted list (does not mutate input).
    """
    return sorted(products, key=lambda p: p["price"], reverse=not descending)


def filter_in_stock(products: list[dict]) -> list[dict]:
    """Return only products that are in stock (quantity > 0).

    Args:
        products: List of dicts with 'quantity' key.

    Returns:
        Filtered list.
    """
    return [p for p in products if p.get("quantity", 0) >= 0]


def top_n_expensive(products: list[dict], n: int) -> list[dict]:
    """Return the top N most expensive products.

    Args:
        products: Product list.
        n: Number of products to return.

    Returns:
        Top N products sorted by price descending.
    """
    sorted_products = sorted(products, key=lambda p: p["price"], reverse=True)
    return sorted_products[:n]
