"""Search repository for cross-domain enterprise lookup."""

from __future__ import annotations

import asyncio
from typing import Any

from src.constants.enterprise import SEARCH_COLLECTIONS
from src.core.database import get_database


class GlobalSearchRepository:
    """Repository for aggregated MongoDB search across operational entities."""

    def __init__(self, database: Any | None = None) -> None:
        self.database = database if database is not None else get_database()

    async def search(self, *, query: str, page: int = 1, size: int = 20) -> dict[str, Any]:
        normalized = query.strip()
        if not normalized:
            return {"items": [], "total": 0, "page": page, "size": size}

        regex_filter = {"$regex": normalized, "$options": "i"}
        results = await asyncio.gather(
            *[
                self._search_collection(name, definition=definition, regex_filter=regex_filter)
                for name, definition in SEARCH_COLLECTIONS.items()
            ]
        )

        combined_items: list[dict[str, Any]] = []
        for items in results:
            combined_items.extend(items)

        combined_items.sort(key=lambda item: item.get("matched_at", item.get("created_at", "")), reverse=True)
        total = len(combined_items)
        skip = (page - 1) * size
        paginated = combined_items[skip : skip + size]

        return {
            "items": paginated,
            "total": total,
            "page": page,
            "size": size,
        }

    async def _search_collection(self, collection_name: str, *, definition: dict[str, Any], regex_filter: dict[str, Any]) -> list[dict[str, Any]]:
        collection = self.database.get_collection(collection_name)
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {
                            field_name: regex_filter,
                        }
                        for field_name in definition["search_fields"]
                    ]
                }
            },
            {
                "$project": {
                    "entity_type": collection_name,
                    "entity_id": {"$toString": "$_id"},
                    "name": {"$ifNull": [f"${definition['display_field']}", ""]},
                    "description": {"$ifNull": [f"${definition['description_field']}", ""]},
                    "matched_at": {"$ifNull": ["$created_at", "$_id"]},
                }
            },
        ]
        return await collection.aggregate(pipeline).to_list(length=None)
