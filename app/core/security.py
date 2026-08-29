"""Безопасность: JWT, пароли."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    user_id: int,
    username: str,
    *,
    is_portal_user: bool = False,
) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "portal": bool(is_portal_user),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token_payload(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as e:
        raise ValueError(str(e)) from e


def decode_token_sub_user_id(token: str) -> int:
    payload = decode_token_payload(token)
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("no sub")
    return int(sub)


def decode_token_is_portal_user(token: str) -> bool:
    try:
        payload = decode_token_payload(token)
    except ValueError:
        return False
    return bool(payload.get("portal", False))
