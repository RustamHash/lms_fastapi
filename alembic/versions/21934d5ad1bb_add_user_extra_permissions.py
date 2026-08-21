"""add user extra_permissions

Revision ID: 21934d5ad1bb
Revises: b08740017c7f
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '21934d5ad1bb'
down_revision: Union[str, Sequence[str], None] = 'b08740017c7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем колонку с server_default для существующих записей
    op.add_column(
        'accounts_user',
        sa.Column(
            'extra_permissions',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment='Дополнительные права пользователя'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('accounts_user', 'extra_permissions')
