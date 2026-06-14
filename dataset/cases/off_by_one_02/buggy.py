"""Pagination utility."""


def paginate(items: list, page: int, page_size: int) -> list:
    """Return a single page of items.

    Args:
        items: Full list of items.
        page: 1-based page number.
        page_size: Number of items per page.

    Returns:
        Sublist for the requested page.
    """
    start = page * page_size
    end = start + page_size
    return items[start:end]


def total_pages(total_items: int, page_size: int) -> int:
    """Calculate total number of pages.

    Args:
        total_items: Total number of items.
        page_size: Items per page.

    Returns:
        Number of pages needed.
    """
    if total_items == 0:
        return 0
    return total_items // page_size
