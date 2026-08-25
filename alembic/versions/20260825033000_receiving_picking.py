"""приёмка/отбор: qty Numeric, связи с заказом, расхождения

Revision ID: 20260825033000
Revises: 20260825025600
Create Date: 2026-08-25 03:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825033000"
down_revision = "20260825025600"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "warehouse_task",
        sa.Column("inbound_order_id", sa.Integer(), nullable=True, comment="Входящий заказ"),
    )
    op.add_column(
        "warehouse_task",
        sa.Column("outbound_order_id", sa.Integer(), nullable=True, comment="Исходящий заказ"),
    )
    op.create_foreign_key(
        "fk_warehouse_task_inbound_order_id",
        "warehouse_task",
        "orders_inbound",
        ["inbound_order_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_warehouse_task_outbound_order_id",
        "warehouse_task",
        "orders_outbound",
        ["outbound_order_id"],
        ["id"],
    )

    op.add_column(
        "warehouse_task_line",
        sa.Column(
            "inbound_order_line_id",
            sa.Integer(),
            nullable=True,
            comment="Строка входящего заказа",
        ),
    )
    op.add_column(
        "warehouse_task_line",
        sa.Column(
            "outbound_order_line_id",
            sa.Integer(),
            nullable=True,
            comment="Строка исходящего заказа",
        ),
    )
    op.add_column(
        "warehouse_task_line",
        sa.Column(
            "reserved",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="Резерв на остатке",
        ),
    )
    op.create_foreign_key(
        "fk_warehouse_task_line_inbound_order_line_id",
        "warehouse_task_line",
        "orders_inbound_line",
        ["inbound_order_line_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_warehouse_task_line_outbound_order_line_id",
        "warehouse_task_line",
        "orders_outbound_line",
        ["outbound_order_line_id"],
        ["id"],
    )
    op.alter_column(
        "warehouse_task_line",
        "plan_qty",
        existing_type=sa.Integer(),
        type_=sa.Numeric(20, 3),
        existing_nullable=False,
    )
    op.alter_column(
        "warehouse_task_line",
        "fact_qty",
        existing_type=sa.Integer(),
        type_=sa.Numeric(20, 3),
        existing_nullable=False,
    )

    op.create_table(
        "warehouse_receiving_discrepancy",
        sa.Column("task_line_id", sa.Integer(), nullable=False, comment="Строка задания"),
        sa.Column("discrepancy_type", sa.String(length=20), nullable=False, comment="shortage / surplus"),
        sa.Column("qty_planned", sa.Numeric(20, 3), nullable=False, comment="План"),
        sa.Column("qty_fact", sa.Numeric(20, 3), nullable=False, comment="Факт"),
        sa.Column("status", sa.String(length=20), nullable=False, comment="Статус"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="ID записи"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False, comment="Активна"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Создана",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Обновлена",
        ),
        sa.Column("created_by_id", sa.Integer(), nullable=True, comment="Создал (user ID)"),
        sa.Column("updated_by_id", sa.Integer(), nullable=True, comment="Изменил (user ID)"),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default="false",
            nullable=False,
            comment="Удалена (soft)",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, comment="Удалена (когда)"),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True, comment="Удалил (user ID)"),
        sa.ForeignKeyConstraint(["task_line_id"], ["warehouse_task_line.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["accounts_user.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["accounts_user.id"]),
        sa.ForeignKeyConstraint(["deleted_by_id"], ["accounts_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("warehouse_receiving_discrepancy")
    op.alter_column(
        "warehouse_task_line",
        "fact_qty",
        existing_type=sa.Numeric(20, 3),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "warehouse_task_line",
        "plan_qty",
        existing_type=sa.Numeric(20, 3),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.drop_constraint(
        "fk_warehouse_task_line_outbound_order_line_id",
        "warehouse_task_line",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_warehouse_task_line_inbound_order_line_id",
        "warehouse_task_line",
        type_="foreignkey",
    )
    op.drop_column("warehouse_task_line", "reserved")
    op.drop_column("warehouse_task_line", "outbound_order_line_id")
    op.drop_column("warehouse_task_line", "inbound_order_line_id")
    op.drop_constraint("fk_warehouse_task_outbound_order_id", "warehouse_task", type_="foreignkey")
    op.drop_constraint("fk_warehouse_task_inbound_order_id", "warehouse_task", type_="foreignkey")
    op.drop_column("warehouse_task", "outbound_order_id")
    op.drop_column("warehouse_task", "inbound_order_id")
