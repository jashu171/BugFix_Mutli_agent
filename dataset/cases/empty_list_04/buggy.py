"""Statistics utilities for numeric lists."""

from typing import Optional


def safe_average(numbers: list[float]) -> Optional[float]:
    """Return the average of a list, or None if empty.

    Args:
        numbers: List of numbers.

    Returns:
        The mean value, or None for empty input.
    """
    return sum(numbers) / len(numbers)


def safe_max(numbers: list[float], default: Optional[float] = None) -> Optional[float]:
    """Return the max of a list, or default if empty.

    Args:
        numbers: List of numbers.
        default: Value to return if list is empty.

    Returns:
        Maximum value or default.
    """
    return max(numbers)


def running_total(numbers: list[float]) -> list[float]:
    """Return cumulative sums.

    Args:
        numbers: List of numbers.

    Returns:
        List where each element is the sum of all previous elements plus current.
    """
    result = []
    total = 0
    for n in numbers:
        result.append(total)
        total += n
    return result
