"""String and date utility functions."""

from typing import Optional


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated.

    Args:
        text: Input string.
        max_length: Maximum total length including suffix.
        suffix: String to append when truncating.

    Returns:
        Truncated string.
    """
    if not text or max_length <= 0:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    Lowercases, replaces spaces with hyphens, removes non-alphanumeric chars
    (except hyphens), and collapses multiple hyphens.

    Args:
        text: Input string.

    Returns:
        URL-safe slug.
    """
    if not text:
        return ""
    slug = text.lower().strip()

    slug = slug.replace(" ", "-")

    slug = "".join(c for c in slug if c.isalnum() or c == "-")

    # BUG: doesn't collapse multiple hyphens
    return slug


def mask_email(email: str) -> str:
    """Mask an email address for display.

    'alice@example.com' -> 'a***e@example.com'

    Args:
        email: Email address string.

    Returns:
        Masked email string.
    """
    if not email or "@" not in email:
        return email or ""
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked = local[0] + "***"
    else:
        masked = local[0] + "***"
    return f"{masked}@{domain}"
