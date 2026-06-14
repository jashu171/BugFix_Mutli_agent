"""Tests for access control utilities."""

from buggy import is_adult, can_access


class TestIsAdult:
    def test_adult(self):
        assert is_adult(18) is True

    def test_minor(self):
        assert is_adult(17) is False

    def test_senior(self):
        assert is_adult(65) is True

    def test_zero(self):
        assert is_adult(0) is False


class TestCanAccess:
    def test_inactive_user(self):
        user = {"active": False, "role": "user", "id": 1}
        resource = {"public": True, "owner_id": 1}
        assert can_access(user, resource) is False

    def test_admin_access(self):
        user = {"active": True, "role": "admin", "id": 1}
        resource = {"public": False, "owner_id": 2}
        assert can_access(user, resource) is True

    def test_public_resource(self):
        user = {"active": True, "role": "user", "id": 1}
        resource = {"public": True, "owner_id": 2}
        assert can_access(user, resource) is True

    def test_owner_access(self):
        user = {"active": True, "role": "user", "id": 1}
        resource = {"public": False, "owner_id": 1}
        assert can_access(user, resource) is True

    def test_non_owner_denied(self):
        user = {"active": True, "role": "user", "id": 1}
        resource = {"public": False, "owner_id": 2}
        assert can_access(user, resource) is False
