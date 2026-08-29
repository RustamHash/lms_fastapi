"""Тесты DataScope: оператор vs портал."""

from __future__ import annotations

from types import SimpleNamespace

from app.accounts.scope import DataScope, build_scope


def _user(*, is_superuser=False, is_portal_user=False, depositor_ids=None, client_ids=None):
    return SimpleNamespace(
        is_superuser=is_superuser,
        is_portal_user=is_portal_user,
        depositor_ids=list(depositor_ids or []),
        client_ids=list(client_ids or []),
    )


def test_operator_unrestricted_even_with_empty_depositors():
    scope = build_scope(_user(is_portal_user=False, depositor_ids=[]))
    assert scope.unrestricted is True
    assert scope.is_portal_user is False
    assert scope.allows_depositor(999) is True


def test_portal_without_bindings_sees_nothing():
    scope = build_scope(_user(is_portal_user=True, depositor_ids=[]))
    assert scope.unrestricted is False
    assert scope.depositor_ids == frozenset()
    assert scope.allows_depositor(1) is False


def test_portal_with_depositor_only_own():
    scope = build_scope(_user(is_portal_user=True, depositor_ids=[5, 7]))
    assert scope.allows_depositor(5) is True
    assert scope.allows_depositor(7) is True
    assert scope.allows_depositor(1) is False


def test_superuser_unrestricted():
    scope = build_scope(
        _user(is_superuser=True, is_portal_user=True, depositor_ids=[1])
    )
    assert scope.unrestricted is True


def test_data_scope_single_depositor_id():
    s = DataScope(unrestricted=False, depositor_ids=frozenset({3}), client_ids=None)
    assert s.single_depositor_id == 3
    s2 = DataScope(unrestricted=False, depositor_ids=frozenset({1, 2}), client_ids=None)
    assert s2.single_depositor_id is None
