"""add_unique_constraints

Revision ID: 20260822014908
Revises: eb645a31cda9
Create Date: 2026-08-22 01:49:08

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260822014929'
down_revision = '20260822014928'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Уникальные ограничения для критических полей
    op.create_unique_constraint('uq_documents_document_number', 'documents_document', ['document_number'])
    op.create_unique_constraint('uq_warehouse_product_depositor_external', 'warehouse_product', ['depositor_id', 'external_id'])
    op.create_unique_constraint('uq_warehouse_lpn_number', 'warehouse_lpn', ['number'])
    op.create_unique_constraint('uq_parties_contract_number', 'parties_contract', ['number'])
    op.create_unique_constraint('uq_delivery_order_number', 'delivery_order', ['number'])
    op.create_unique_constraint('uq_delivery_route_number', 'delivery_route', ['number'])
    op.create_unique_constraint('uq_warehouse_warehouse_name', 'warehouse_warehouse', ['name'])
    op.create_unique_constraint('uq_warehouse_zone_name', 'warehouse_zone', ['name'])


def downgrade() -> None:
    op.drop_constraint('uq_documents_document_number', 'documents_document', type_='unique')
    op.drop_constraint('uq_warehouse_product_depositor_external', 'warehouse_product', type_='unique')
    op.drop_constraint('uq_warehouse_lpn_number', 'warehouse_lpn', type_='unique')
    op.drop_constraint('uq_parties_contract_number', 'parties_contract', type_='unique')
    op.drop_constraint('uq_delivery_order_number', 'delivery_order', type_='unique')
    op.drop_constraint('uq_delivery_route_number', 'delivery_route', type_='unique')
    op.drop_constraint('uq_warehouse_warehouse_name', 'warehouse_warehouse', type_='unique')
    op.drop_constraint('uq_warehouse_zone_name', 'warehouse_zone', type_='unique')
