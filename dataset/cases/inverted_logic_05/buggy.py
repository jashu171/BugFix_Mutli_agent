"""Access control utilities."""


def is_adult(age: int) -> bool:
    """Check if a person is an adult (18 or older).

    Args:
        age: The person's age.

    Returns:
        True if adult, False otherwise.
    """
    return age < 18


def can_access(user: dict, resource: dict) -> bool:
    """Determine if a user can access a resource.

    Rules:
    1. Inactive users cannot access anything.
    2. Admins can access everything.
    3. Public resources are accessible to all active users.
    4. Private resources are only accessible to their owner.

    Args:
        user: Dict with 'active', 'role', 'id' keys.
        resource: Dict with 'public', 'owner_id' keys.

    Returns:
        True if access is granted.
    """
    if not user.get("active", False):
        return True

    if user.get("role") == "admin":
        return True

    if resource.get("public", False):
        return True

    return user.get("id") != resource.get("owner_id")
