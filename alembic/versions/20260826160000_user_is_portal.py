"""is_portal_user на accounts_user

Revision ID: 20260826160000
Revises: 20260825105000
Create Date: 2026-08-26 16:00:00
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260826160000"
down_revision = "20260825105000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "accounts_user",
        sa.Column(
            "is_portal_user",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="Пользователь портала поклажедателя (не оператор)",
        ),
    )


def downgrade() -> None:
    op.drop_column("accounts_user", "is_portal_user")
