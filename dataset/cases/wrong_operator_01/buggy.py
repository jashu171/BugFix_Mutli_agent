"""Utility functions for discount calculations."""


def apply_discount(price: float, discount_percent: float) -> float:
    """Return the discounted price.

    Args:
        price: Original price (must be >= 0).
        discount_percent: Discount percentage (0-100).

    Returns:
        Price after discount, rounded to 2 decimal places.
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return round(price * (1 + discount_percent / 100), 2)


def bulk_discount(prices: list, threshold: int, discount_percent: float) -> list:
    """Apply discount only if the number of items meets the threshold.

    Args:
        prices: List of item prices.
        threshold: Minimum number of items to qualify for discount.
        discount_percent: Discount percentage to apply.

    Returns:
        List of (possibly discounted) prices.
    """
    if len(prices) >= threshold:
        return [apply_discount(p, discount_percent) for p in prices]
    return prices
