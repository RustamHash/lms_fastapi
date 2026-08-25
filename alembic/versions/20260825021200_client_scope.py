"""accounts: client_id на заказах, user_client

Revision ID: 20260825021200
Revises: 20260825014300
Create Date: 2026-08-25 02:12:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825021200"
down_revision = "20260825014300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE orders_outbound o
        SET client_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE o.client_id IS NULL
          AND o.depositor_id = c.depositor_id
          AND c.code = left(o.customer_code, 50)
          AND o.customer_code <> ''
        """
    )
    op.execute(
        """
        INSERT INTO parties_client (
            depositor_id, code, name, legal_name, inn, kpp, is_edo
        )
        SELECT DISTINCT
            o.depositor_id,
            CASE WHEN o.customer_code = '' THEN 'UNKNOWN' ELSE left(o.customer_code, 50) END,
            CASE WHEN o.customer_name = '' THEN 'Клиент' ELSE left(o.customer_name, 255) END,
            '', '', '', false
        FROM orders_outbound o
        WHERE o.client_id IS NULL
          AND NOT EXISTS (
            SELECT 1 FROM parties_client c
            WHERE c.depositor_id = o.depositor_id
              AND c.code = CASE WHEN o.customer_code = '' THEN 'UNKNOWN' ELSE left(o.customer_code, 50) END
              AND c.is_deleted = false
          )
        """
    )
    op.execute(
        """
        UPDATE orders_outbound o
        SET client_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE o.client_id IS NULL
          AND o.depositor_id = c.depositor_id
          AND c.code = CASE WHEN o.customer_code = '' THEN 'UNKNOWN' ELSE left(o.customer_code, 50) END
        """
    )
    op.alter_column(
        "orders_outbound",
        "client_id",
        existing_type=sa.Integer(),
        nullable=False,
        comment="Клиент",
    )

    op.add_column(
        "orders_return",
        sa.Column("client_id", sa.Integer(), nullable=True, comment="Клиент"),
    )
    op.create_foreign_key(
        "orders_return_client_id_fkey",
        "orders_return",
        "parties_client",
        ["client_id"],
        ["id"],
    )
    op.execute(
        """
        UPDATE orders_return r
        SET client_id = o.client_id
        FROM orders_outbound o
        WHERE r.outbound_order_id = o.id
          AND r.client_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE orders_return r
        SET client_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE r.client_id IS NULL
          AND r.depositor_id = c.depositor_id
          AND c.code = CASE WHEN r.customer_code = '' THEN 'UNKNOWN' ELSE left(r.customer_code, 50) END
        """
    )
    op.execute(
        """
        INSERT INTO parties_client (
            depositor_id, code, name, legal_name, inn, kpp, is_edo
        )
        SELECT DISTINCT
            r.depositor_id,
            CASE WHEN r.customer_code = '' THEN 'UNKNOWN' ELSE left(r.customer_code, 50) END,
            CASE WHEN r.customer_name = '' THEN 'Клиент' ELSE left(r.customer_name, 255) END,
            '', '', '', false
        FROM orders_return r
        WHERE r.client_id IS NULL
          AND NOT EXISTS (
            SELECT 1 FROM parties_client c
            WHERE c.depositor_id = r.depositor_id
              AND c.code = CASE WHEN r.customer_code = '' THEN 'UNKNOWN' ELSE left(r.customer_code, 50) END
              AND c.is_deleted = false
          )
        """
    )
    op.execute(
        """
        UPDATE orders_return r
        SET client_id = c.id
        FROM (
            SELECT DISTINCT ON (depositor_id, code)
                id, depositor_id, code
            FROM parties_client
            WHERE is_deleted = false
            ORDER BY depositor_id, code, id
        ) c
        WHERE r.client_id IS NULL
          AND r.depositor_id = c.depositor_id
          AND c.code = CASE WHEN r.customer_code = '' THEN 'UNKNOWN' ELSE left(r.customer_code, 50) END
        """
    )
    op.alter_column(
        "orders_return",
        "client_id",
        existing_type=sa.Integer(),
        nullable=False,
        comment="Клиент",
    )

    op.create_table(
        "accounts_user_client",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="Пользователь"),
        sa.Column("client_id", sa.Integer(), nullable=False, comment="Клиент"),
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
        sa.ForeignKeyConstraint(["client_id"], ["parties_client.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["accounts_user.id"]),
        sa.ForeignKeyConstraint(["deleted_by_id"], ["accounts_user.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["accounts_user.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["accounts_user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "client_id", name="uq_user_client"),
    )


def downgrade() -> None:
    op.drop_table("accounts_user_client")
    op.drop_constraint("orders_return_client_id_fkey", "orders_return", type_="foreignkey")
    op.drop_column("orders_return", "client_id")
    op.alter_column(
        "orders_outbound",
        "client_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="Клиент",
    )
