"""add_indexes_for_frequent_fields

Revision ID: 20260822014908
Revises: eb645a31cda9
Create Date: 2026-08-22 01:49:08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260822014928'
down_revision = '83eea76fb8df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Индексы для часто используемых полей
    op.create_index('ix_orders_inbound_number', 'orders_inbound', ['number'])
    op.create_index('ix_orders_outbound_number', 'orders_outbound', ['number'])
    op.create_index('ix_orders_outbound_document_number', 'orders_outbound', ['document_number'])
    op.create_index('ix_documents_document_number', 'documents_document', ['document_number'])
    op.create_index('ix_warehouse_product_external_id', 'warehouse_product', ['external_id'])
    op.create_index('ix_warehouse_product_sku', 'warehouse_product', ['sku'])
    op.create_index('ix_delivery_order_number', 'delivery_order', ['number'])
    op.create_index('ix_parties_client_code', 'parties_client', ['code'])
    op.create_index('ix_parties_contract_number', 'parties_contract', ['number'])
    op.create_index('ix_warehouse_batch_number', 'warehouse_batch', ['batch_number'])
    # ix_warehouse_lpn_number уже существует (unique=True)
    op.create_index('ix_integration_profile_name', 'integration_profile', ['name'])
    # ix_accounts_user_username уже существует (unique=True)
    # ix_accounts_role_code уже существует (unique=True)
    op.create_index('ix_warehouse_warehouse_name', 'warehouse_warehouse', ['name'])
    
    # Композитные индексы для частых запросов
    op.create_index('ix_orders_inbound_depositor_number', 'orders_inbound', ['depositor_id', 'number'])
    op.create_index('ix_orders_outbound_depositor_number', 'orders_outbound', ['depositor_id', 'number'])
    op.create_index('ix_warehouse_product_depositor_external', 'warehouse_product', ['depositor_id', 'external_id'])
    op.create_index('ix_documents_document_warehouse', 'documents_document', ['warehouse_id'])
    op.create_index('ix_orders_outbound_status', 'orders_outbound', ['status'])
    op.create_index('ix_orders_inbound_status', 'orders_inbound', ['status'])
    op.create_index('ix_delivery_order_status', 'delivery_order', ['status'])
    op.create_index('ix_warehouse_task_status', 'warehouse_task', ['status'])


def downgrade() -> None:
    op.drop_index('ix_orders_inbound_number', table_name='orders_inbound')
    op.drop_index('ix_orders_outbound_number', table_name='orders_outbound')
    op.drop_index('ix_orders_outbound_document_number', table_name='orders_outbound')
    op.drop_index('ix_documents_document_number', table_name='documents_document')
    op.drop_index('ix_warehouse_product_external_id', table_name='warehouse_product')
    op.drop_index('ix_warehouse_product_sku', table_name='warehouse_product')
    op.drop_index('ix_delivery_order_number', table_name='delivery_order')
    op.drop_index('ix_parties_client_code', table_name='parties_client')
    op.drop_index('ix_parties_contract_number', table_name='parties_contract')
    op.drop_index('ix_warehouse_batch_number', table_name='warehouse_batch')
    # ix_warehouse_lpn_number уже существует (unique=True)
    op.drop_index('ix_integration_profile_name', table_name='integration_profile')
    # ix_accounts_user_username уже существует (unique=True)
    # ix_accounts_role_code уже существует (unique=True)
    op.drop_index('ix_warehouse_warehouse_name', table_name='warehouse_warehouse')
    op.drop_index('ix_orders_inbound_depositor_number', table_name='orders_inbound')
    op.drop_index('ix_orders_outbound_depositor_number', table_name='orders_outbound')
    op.drop_index('ix_warehouse_product_depositor_external', table_name='warehouse_product')
    op.drop_index('ix_documents_document_warehouse', table_name='documents_document')
    op.drop_index('ix_orders_outbound_status', table_name='orders_outbound')
    op.drop_index('ix_orders_inbound_status', table_name='orders_inbound')
    op.drop_index('ix_delivery_order_status', table_name='delivery_order')
    op.drop_index('ix_warehouse_task_status', table_name='warehouse_task')
