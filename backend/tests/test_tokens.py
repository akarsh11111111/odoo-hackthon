from src.core.config import get_settings
from src.core.security import create_access_token, create_refresh_token, decode_token, hash_password, hash_refresh_token, verify_password, verify_refresh_token


def test_password_hash_round_trip() -> None:
    password = "Str0ng!Pass123"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_refresh_token_hash_is_deterministic(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    hashed_one = hash_refresh_token("refresh-token-value")
    hashed_two = hash_refresh_token("refresh-token-value")

    assert hashed_one == hashed_two
    assert verify_refresh_token("refresh-token-value", hashed_one) is True


def test_access_and_refresh_token_round_trip(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-sufficient-length-12345")
    get_settings.cache_clear()

    access_token, _ = create_access_token(subject="user-id", role_name="Fleet Manager", email="alex@example.com")
    refresh_token, _ = create_refresh_token(subject="user-id", role_name="Fleet Manager", email="alex@example.com")

    access_payload = decode_token(access_token, expected_type="access")
    refresh_payload = decode_token(refresh_token, expected_type="refresh")

    assert access_payload["sub"] == "user-id"
    assert refresh_payload["token_type"] == "refresh"
