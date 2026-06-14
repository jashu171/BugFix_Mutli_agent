"""Temperature conversion and range utilities."""


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit.

    Args:
        celsius: Temperature in Celsius.

    Returns:
        Temperature in Fahrenheit, rounded to 1 decimal place.
    """
    return round(celsius * 9 / 5 + 32, 1)


def is_in_range(value: float, low: float, high: float) -> bool:
    """Check if value is within [low, high] inclusive.

    Args:
        value: The value to check.
        low: Lower bound (inclusive).
        high: Upper bound (inclusive).

    Returns:
        True if low <= value <= high.
    """
    return low < value < high


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to the range [low, high].

    Args:
        value: The value to clamp.
        low: Minimum allowed value.
        high: Maximum allowed value.

    Returns:
        Clamped value.
    """
    if value < low:
        return low
    if value > high:
        return low
    return value
