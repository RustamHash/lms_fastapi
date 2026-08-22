"""remove trade_point_id from delivery_order

Revision ID: 20260822145945
Revises: 20260822014929
Create Date: 2026-08-22 14:59:45
"""
from alembic import op
import sqlalchemy as sa

revision = '20260822145945'
down_revision = '20260822014929'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Удаляем FK и колонку
    op.drop_constraint('delivery_order_trade_point_id_fkey', 'delivery_order', type_='foreignkey')
    op.drop_column('delivery_order', 'trade_point_id')


def downgrade() -> None:
    op.add_column('delivery_order', sa.Column('trade_point_id', sa.Integer(), nullable=True))
    op.create_foreign_key('delivery_order_trade_point_id_fkey', 'delivery_order', 'parties_trade_point', ['trade_point_id'], ['id'])
