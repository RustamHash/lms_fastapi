"""inbound: supplier_id обязателен

Revision ID: 20260825104400
Revises: 20260825033000
Create Date: 2026-08-25 10:44:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825104400"
down_revision = "20260825033000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE orders_inbound o
        SET supplier_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE o.supplier_id IS NULL
          AND o.depositor_id = c.depositor_id
          AND c.code = left(o.supplier_code, 50)
          AND o.supplier_code <> ''
        """
    )
    op.execute(
        """
        INSERT INTO parties_client (
            depositor_id, code, name, legal_name, inn, kpp, is_edo
        )
        SELECT DISTINCT
            o.depositor_id,
            CASE WHEN o.supplier_code = '' THEN 'UNKNOWN' ELSE left(o.supplier_code, 50) END,
            'Поставщик',
            '', '', '', false
        FROM orders_inbound o
        WHERE o.supplier_id IS NULL
          AND NOT EXISTS (
            SELECT 1 FROM parties_client c
            WHERE c.depositor_id = o.depositor_id
              AND c.code = CASE WHEN o.supplier_code = '' THEN 'UNKNOWN' ELSE left(o.supplier_code, 50) END
              AND c.is_deleted = false
          )
        """
    )
    op.execute(
        """
        UPDATE orders_inbound o
        SET supplier_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE o.supplier_id IS NULL
          AND o.depositor_id = c.depositor_id
          AND c.code = CASE WHEN o.supplier_code = '' THEN 'UNKNOWN' ELSE left(o.supplier_code, 50) END
        """
    )
    op.alter_column(
        "orders_inbound",
        "supplier_id",
        existing_type=sa.Integer(),
        nullable=False,
        comment="Поставщик",
    )


def downgrade() -> None:
    op.alter_column(
        "orders_inbound",
        "supplier_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="Поставщик",
    )
