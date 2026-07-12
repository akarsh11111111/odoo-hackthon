"""Authentication and authorization API routes."""

from fastapi import APIRouter, Depends, status

from src.dependencies.auth import get_current_active_user, get_current_user
from src.models.auth import User
from src.schemas.auth import (
    AuthMessageResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetResponse,
    SessionResponse,
)
from src.schemas.common import build_response
from src.services.auth import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Create a new TransitOps user and issue a JWT session.",
)
async def register_user(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    session = await auth_service.register(payload)
    return build_response(success=True, message="User registered successfully", data=session)


@router.post(
    "/login",
    response_model=RegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate a user and return a new access and refresh token pair.",
)
async def login_user(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    session = await auth_service.login(payload)
    return build_response(success=True, message="Login successful", data=session)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke the presented refresh token so it can no longer be used.",
)
async def logout_user(
    payload: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    result = await auth_service.logout(payload)
    return build_response(success=True, message="Logout successful", data=AuthMessageResponse(**result))


@router.post(
    "/refresh",
    response_model=RegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh tokens",
    description="Rotate a refresh token and issue a new access and refresh token pair.",
)
async def refresh_tokens(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    session = await auth_service.refresh(payload)
    return build_response(success=True, message="Token refreshed successfully", data=session)


@router.post(
    "/forgot-password",
    response_model=ResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Start password reset",
    description="Generate a short-lived password reset token for the provided email address.",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ResetResponse:
    result = await auth_service.forgot_password(payload)
    return build_response(success=True, message="Password reset flow started", data=result)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Complete the password reset flow using a short-lived reset token.",
)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    result = await auth_service.reset_password(payload)
    return build_response(success=True, message="Password reset successful", data=AuthMessageResponse(**result))


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change the password for the currently authenticated user.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    result = await auth_service.change_password(current_user, payload)
    return build_response(success=True, message="Password changed successfully", data=AuthMessageResponse(**result))


@router.get(
    "/me",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Current user",
    description="Return the authenticated user's profile and role information.",
)
async def current_user_profile(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionResponse:
    user = await auth_service.get_current_user(current_user)
    return build_response(success=True, message="Current user fetched successfully", data=user)
