"""документ: связь с входящим заказом

Revision ID: 20260825025600
Revises: 20260825024900
Create Date: 2026-08-25 02:56:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825025600"
down_revision = "20260825024900"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents_document",
        sa.Column(
            "inbound_order_id",
            sa.Integer(),
            nullable=True,
            comment="Входящий заказ",
        ),
    )
    op.create_foreign_key(
        "fk_documents_document_inbound_order_id",
        "documents_document",
        "orders_inbound",
        ["inbound_order_id"],
        ["id"],
    )
    op.create_index(
        "ix_documents_document_inbound_order_id",
        "documents_document",
        ["inbound_order_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_document_inbound_order_id",
        table_name="documents_document",
    )
    op.drop_constraint(
        "fk_documents_document_inbound_order_id",
        "documents_document",
        type_="foreignkey",
    )
    op.drop_column("documents_document", "inbound_order_id")
