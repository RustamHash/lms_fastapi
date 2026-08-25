from datetime import date
from decimal import Decimal

from app.warehouse.services.plan_fact_view import remaining_shelf_life


def test_remaining_shelf_life_days_and_percent() -> None:
    result = remaining_shelf_life(
        production_date=date(2026, 1, 1),
        expiration_date=date(2026, 4, 1),
        as_of=date(2026, 2, 1),
    )
    assert result["remaining_days"] == 59
    assert result["remaining_percent"] == Decimal("65.6")


def test_remaining_shelf_life_without_production() -> None:
    result = remaining_shelf_life(
        production_date=None,
        expiration_date=date(2026, 4, 1),
        as_of=date(2026, 2, 1),
    )
    assert result["remaining_days"] == 59
    assert result["remaining_percent"] is None


def test_remaining_shelf_life_without_expiration() -> None:
    result = remaining_shelf_life(
        production_date=date(2026, 1, 1),
        expiration_date=None,
        as_of=date(2026, 2, 1),
    )
    assert result["remaining_days"] is None
    assert result["remaining_percent"] is None
