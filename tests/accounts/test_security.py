"""JWT portal claim + soft-delete unit checks без БД."""

from __future__ import annotations

from app.core.security import (
    create_access_token,
    decode_token_is_portal_user,
    decode_token_sub_user_id,
)


def test_access_token_portal_claim():
    token = create_access_token(42, "portal_user", is_portal_user=True)
    assert decode_token_sub_user_id(token) == 42
    assert decode_token_is_portal_user(token) is True


def test_access_token_operator_claim():
    token = create_access_token(7, "ops", is_portal_user=False)
    assert decode_token_is_portal_user(token) is False
