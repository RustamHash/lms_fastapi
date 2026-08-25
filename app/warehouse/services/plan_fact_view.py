from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def discrepancy_kind(planned: Decimal, fact: Decimal) -> str:
    if fact == planned:
        return "match"
    return "shortage" if fact < planned else "surplus"


def product_label(product) -> dict[str, str]:
    if product is None:
        return {"product_sku": "", "product_name": ""}
    return {
        "product_sku": product.sku or "",
        "product_name": product.name or "",
    }


def remaining_shelf_life(
    *,
    production_date: date | None,
    expiration_date: date | None,
    as_of: date | None = None,
) -> dict:
    """Остаток срока годности партии на дату as_of (по умолчанию сегодня)."""
    as_of = as_of or date.today()
    remaining_days: int | None = None
    remaining_percent: Decimal | None = None
    if expiration_date is not None:
        remaining_days = (expiration_date - as_of).days
        if production_date is not None:
            total_days = (expiration_date - production_date).days
            if total_days > 0:
                remaining_percent = (
                    Decimal(remaining_days) * 100 / Decimal(total_days)
                ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return {
        "production_date": production_date,
        "expiration_date": expiration_date,
        "remaining_days": remaining_days,
        "remaining_percent": remaining_percent,
    }


def movement_row(move) -> dict:
    batch = move.batch
    lpn = move.lpn
    production_date = batch.production_date if batch else None
    expiration_date = batch.expiration_date if batch else None
    return {
        "id": move.id,
        "moved_at": move.moved_at,
        "direction": move.direction,
        "quantity": move.quantity,
        "product_id": move.product_id,
        **product_label(move.product),
        "batch_number": batch.batch_number if batch else "",
        "lpn_number": lpn.number if lpn else "",
        "location_id": move.location_id,
        "task_line_id": move.task_line_id,
        **remaining_shelf_life(
            production_date=production_date,
            expiration_date=expiration_date,
        ),
    }
