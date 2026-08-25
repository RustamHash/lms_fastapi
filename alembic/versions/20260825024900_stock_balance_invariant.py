"""остаток: LPN обязателен, unique, CHECK; движение moved_at

Revision ID: 20260825024900
Revises: 20260825021200
Create Date: 2026-08-25 02:49:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825024900"
down_revision = "20260825021200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH dupes AS (
            SELECT
                product_id,
                location_id,
                batch_id,
                lpn_id,
                MIN(id) AS keep_id,
                SUM(quantity) AS qty,
                SUM(reserved_quantity) AS reserved
            FROM warehouse_stock_balance
            GROUP BY product_id, location_id, batch_id, lpn_id
            HAVING COUNT(*) > 1
        )
        UPDATE warehouse_stock_balance b
        SET
            quantity = GREATEST(d.qty, 0),
            reserved_quantity = LEAST(GREATEST(d.reserved, 0), GREATEST(d.qty, 0))
        FROM dupes d
        WHERE b.id = d.keep_id
        """
    )
    op.execute(
        """
        DELETE FROM warehouse_stock_balance b
        USING (
            SELECT
                product_id,
                location_id,
                batch_id,
                lpn_id,
                MIN(id) AS keep_id
            FROM warehouse_stock_balance
            GROUP BY product_id, location_id, batch_id, lpn_id
            HAVING COUNT(*) > 1
        ) d
        WHERE b.product_id = d.product_id
          AND b.location_id = d.location_id
          AND b.batch_id = d.batch_id
          AND b.lpn_id IS NOT DISTINCT FROM d.lpn_id
          AND b.id <> d.keep_id
        """
    )
    op.execute(
        """
        WITH ins AS (
            INSERT INTO warehouse_lpn (number, status)
            SELECT left('AUTO-' || b.id::text, 20), 'created'
            FROM warehouse_stock_balance b
            WHERE b.lpn_id IS NULL
            RETURNING id, number
        )
        UPDATE warehouse_stock_balance b
        SET lpn_id = ins.id
        FROM ins
        WHERE b.lpn_id IS NULL
          AND ins.number = left('AUTO-' || b.id::text, 20)
        """
    )
    op.execute(
        """
        UPDATE warehouse_stock_balance
        SET quantity = 0
        WHERE quantity < 0
        """
    )
    op.execute(
        """
        UPDATE warehouse_stock_balance
        SET reserved_quantity = 0
        WHERE reserved_quantity < 0
        """
    )
    op.execute(
        """
        UPDATE warehouse_stock_balance
        SET reserved_quantity = quantity
        WHERE reserved_quantity > quantity
        """
    )

    op.alter_column("warehouse_stock_balance", "lpn_id", nullable=False)
    op.create_unique_constraint(
        "uq_stock_balance_key",
        "warehouse_stock_balance",
        ["product_id", "location_id", "batch_id", "lpn_id"],
    )
    op.create_check_constraint(
        "ck_stock_balance_quantity_non_negative",
        "warehouse_stock_balance",
        "quantity >= 0",
    )
    op.create_check_constraint(
        "ck_stock_balance_reserved_non_negative",
        "warehouse_stock_balance",
        "reserved_quantity >= 0",
    )
    op.create_check_constraint(
        "ck_stock_balance_reserved_le_quantity",
        "warehouse_stock_balance",
        "reserved_quantity <= quantity",
    )
    op.create_index(
        "ix_stock_balance_product_location",
        "warehouse_stock_balance",
        ["product_id", "location_id"],
    )

    op.add_column(
        "warehouse_stock_movement",
        sa.Column("moved_at", sa.DateTime(timezone=True), nullable=True, comment="Момент движения"),
    )
    op.add_column(
        "warehouse_stock_movement",
        sa.Column("moved_by_id", sa.Integer(), nullable=True, comment="Кто двигал"),
    )
    op.add_column(
        "warehouse_stock_movement",
        sa.Column("task_line_id", sa.Integer(), nullable=True, comment="Строка задания"),
    )
    op.execute("UPDATE warehouse_stock_movement SET moved_at = created_at WHERE moved_at IS NULL")
    op.alter_column("warehouse_stock_movement", "moved_at", nullable=False)
    op.create_foreign_key(
        "fk_stock_movement_moved_by_id",
        "warehouse_stock_movement",
        "accounts_user",
        ["moved_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_stock_movement_task_line_id",
        "warehouse_stock_movement",
        "warehouse_task_line",
        ["task_line_id"],
        ["id"],
    )
    op.create_index("ix_stock_movement_moved_at", "warehouse_stock_movement", ["moved_at"])


def downgrade() -> None:
    op.drop_index("ix_stock_movement_moved_at", table_name="warehouse_stock_movement")
    op.drop_constraint("fk_stock_movement_task_line_id", "warehouse_stock_movement", type_="foreignkey")
    op.drop_constraint("fk_stock_movement_moved_by_id", "warehouse_stock_movement", type_="foreignkey")
    op.drop_column("warehouse_stock_movement", "task_line_id")
    op.drop_column("warehouse_stock_movement", "moved_by_id")
    op.drop_column("warehouse_stock_movement", "moved_at")

    op.drop_index("ix_stock_balance_product_location", table_name="warehouse_stock_balance")
    op.drop_constraint("ck_stock_balance_reserved_le_quantity", "warehouse_stock_balance", type_="check")
    op.drop_constraint("ck_stock_balance_reserved_non_negative", "warehouse_stock_balance", type_="check")
    op.drop_constraint("ck_stock_balance_quantity_non_negative", "warehouse_stock_balance", type_="check")
    op.drop_constraint("uq_stock_balance_key", "warehouse_stock_balance", type_="unique")
    op.alter_column("warehouse_stock_balance", "lpn_id", nullable=True)
