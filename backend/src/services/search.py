"""Global search service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.repositories.search import GlobalSearchRepository


@dataclass(slots=True)
class GlobalSearchService:
    """Cross-domain search service for vehicles, drivers, trips, maintenance, fuel, and expense records."""

    repository: GlobalSearchRepository

    async def search(
        self,
        *,
        query: str,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        return await self.repository.search(query=query, page=page, size=size)


def get_search_service() -> GlobalSearchService:
    """Build a search service with the active repository dependency."""

    return GlobalSearchService(repository=GlobalSearchRepository())
