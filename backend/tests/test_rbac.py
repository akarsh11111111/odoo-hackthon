from dataclasses import dataclass

import pytest

from src.core.exceptions import ForbiddenException
from src.dependencies.auth import require_role
from src.repositories.auth import RoleRepository


@dataclass
class FakeRole:
    id: str
    role_name: str


@dataclass
class FakeUser:
    id: str
    is_active: bool = True
    role_id: str = "role-1"


@pytest.mark.asyncio
async def test_require_role_allows_matching_role(monkeypatch) -> None:
    dependency = require_role("Fleet Manager")

    async def fake_get_by_id(self, _: str):
        return FakeRole(id="role-1", role_name="Fleet Manager")

    monkeypatch.setattr(RoleRepository, "get_by_id", fake_get_by_id, raising=False)

    result = await dependency(current_user=FakeUser(id="user-1"))

    assert result.id == "user-1"


@pytest.mark.asyncio
async def test_require_role_denies_mismatched_role(monkeypatch) -> None:
    dependency = require_role("Fleet Manager")

    async def fake_get_by_id(self, _: str):
        return FakeRole(id="role-1", role_name="Dispatcher")

    monkeypatch.setattr(RoleRepository, "get_by_id", fake_get_by_id, raising=False)

    with pytest.raises(ForbiddenException):
        await dependency(current_user=FakeUser(id="user-1"))
