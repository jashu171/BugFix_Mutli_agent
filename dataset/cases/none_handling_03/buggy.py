"""User profile utilities."""

from typing import Optional


def get_display_name(user: dict) -> str:
    """Return a display name from a user dict.

    Priority: full_name > username > email prefix > 'Anonymous'

    Args:
        user: Dict with optional keys 'full_name', 'username', 'email'.

    Returns:
        A display string.
    """
    if user.get("full_name"):
        return user["full_name"]
    if user.get("username"):
        return user["username"]
    if user.get("email"):
        return user["email"].split("@")[0]
    return "Anonymous"


def format_greeting(user: dict, time_of_day: str) -> str:
    """Return a greeting string.

    Args:
        user: User dict or None.
        time_of_day: One of 'morning', 'afternoon', 'evening'.

    Returns:
        Greeting like 'Good morning, Alice!'
    """
    name = get_display_name(user)
    return f"Good {time_of_day}, {name}!"
