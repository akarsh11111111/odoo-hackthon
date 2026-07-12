"""Authentication and authorization constants."""

from typing import Final

FLEET_MANAGER: Final[str] = "Fleet Manager"
DISPATCHER: Final[str] = "Driver"
SAFETY_OFFICER: Final[str] = "Safety Officer"
FINANCIAL_ANALYST: Final[str] = "Financial Analyst"

ROLE_NAMES: Final[tuple[str, ...]] = (
    FLEET_MANAGER,
    DISPATCHER,
    SAFETY_OFFICER,
    FINANCIAL_ANALYST,
)

DEFAULT_ROLE_PERMISSIONS: Final[dict[str, list[str]]] = {
    FLEET_MANAGER: [
        "vehicles:read",
        "vehicles:write",
        "drivers:read",
        "drivers:write",
        "trips:read",
        "reports:read",
    ],
    DISPATCHER: ["trips:read", "trips:write"],
    SAFETY_OFFICER: ["drivers:read", "drivers:write"],
    FINANCIAL_ANALYST: ["reports:read"],
}
