"""inbound: loc_code (LOC) обязателен, order_number опционален

Revision ID: 20260825105000
Revises: 20260825104400
Create Date: 2026-08-25 10:50:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825105000"
down_revision = "20260825104400"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders_inbound",
        sa.Column(
            "order_number",
            sa.String(length=100),
            nullable=False,
            server_default="",
            comment="Номер заказа",
        ),
    )
    op.add_column(
        "orders_inbound",
        sa.Column(
            "loc_code",
            sa.String(length=50),
            nullable=False,
            server_default="",
            comment="Код склада (LOC)",
        ),
    )
    op.execute(
        """
        UPDATE orders_inbound
        SET loc_code = btrim(substring(notes from '^LOC:[[:space:]]*(.*)$'))
        WHERE notes ~ '^LOC:'
          AND btrim(substring(notes from '^LOC:[[:space:]]*(.*)$')) <> ''
        """
    )
    op.alter_column("orders_inbound", "order_number", server_default=None)
    op.alter_column("orders_inbound", "loc_code", server_default=None)


def downgrade() -> None:
    op.drop_column("orders_inbound", "loc_code")
    op.drop_column("orders_inbound", "order_number")
