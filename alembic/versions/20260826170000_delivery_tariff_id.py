"""nullable tariff_id on delivery_order

Revision ID: 20260826170000
Revises: 20260826160000
Create Date: 2026-08-26 17:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260826170000"
down_revision = "20260826160000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "delivery_order",
        sa.Column(
            "tariff_id",
            sa.Integer(),
            sa.ForeignKey("parties_tariff.id"),
            nullable=True,
            comment="Тариф доставки",
        ),
    )


def downgrade() -> None:
    op.drop_column("delivery_order", "tariff_id")
