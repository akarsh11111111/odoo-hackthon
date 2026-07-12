"""Health endpoints for TransitOps."""

from fastapi import APIRouter, status

from src.schemas.common import APIResponse, build_response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=APIResponse[dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns service status and confirms the API is running.",
)
async def health_check() -> APIResponse[dict[str, str]]:
    """Return a basic uptime response for infrastructure checks."""

    return build_response(
        success=True,
        message="TransitOps API is running",
        data={"status": "ok", "service": "TransitOps"},
    )
