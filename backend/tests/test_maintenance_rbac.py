from __future__ import annotations

import pytest

from src.constants.auth import DISPATCHER, FLEET_MANAGER, FINANCIAL_ANALYST, SAFETY_OFFICER
from src.core.exceptions import ForbiddenException
from src.dependencies.auth import require_role
from src.repositories.auth import RoleRepository


class FakeRole:
    def __init__(self, role_name: str) -> None:
        self.role_name = role_name


class FakeUser:
    def __init__(self, user_id: str = "user-1", is_active: bool = True) -> None:
        self.id = user_id
        self.is_active = is_active
        self.role_id = "role-1"


@pytest.mark.asyncio
async def test_require_role_allows_fleet_manager(monkeypatch) -> None:
    dependency = require_role(FLEET_MANAGER)

    async def fake_get_by_id(self, _: str):
        return FakeRole(FLEET_MANAGER)

    monkeypatch.setattr(RoleRepository, "get_by_id", fake_get_by_id, raising=False)

    result = await dependency(current_user=FakeUser())

    assert result.id == "user-1"


@pytest.mark.asyncio
async def test_require_role_denies_non_fleet_manager(monkeypatch) -> None:
    dependency = require_role(FLEET_MANAGER)

    async def fake_get_by_id(self, _: str):
        return FakeRole(DISPATCHER)

    monkeypatch.setattr(RoleRepository, "get_by_id", fake_get_by_id, raising=False)

    with pytest.raises(ForbiddenException):
        await dependency(current_user=FakeUser())
