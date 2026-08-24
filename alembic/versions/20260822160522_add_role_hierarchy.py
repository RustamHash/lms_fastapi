"""add role hierarchy

Revision ID: 20260822160522
Revises: 20260822145945
Create Date: 2026-08-22 16:05:22
"""
from alembic import op
import sqlalchemy as sa

revision = '20260822160522'
down_revision = '20260822145945'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('accounts_role', sa.Column('parent_role_id', sa.Integer(), sa.ForeignKey('accounts_role.id'), nullable=True))


def downgrade() -> None:
    op.drop_constraint('accounts_role_parent_role_id_fkey', 'accounts_role', type_='foreignkey')
    op.drop_column('accounts_role', 'parent_role_id')
