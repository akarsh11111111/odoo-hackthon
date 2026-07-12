"""Global search API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """Cross-domain search result entry."""

    entity_type: str
    entity_id: str
    name: str
    description: str | None = None
    matched_at: str | None = None


class GlobalSearchResponse(BaseModel):
    """Paginated global search response."""

    items: list[SearchResultItem]
    total: int
    page: int
    size: int
