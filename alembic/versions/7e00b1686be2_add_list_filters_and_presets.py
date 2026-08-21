"""add list filters and presets

Revision ID: 7e00b1686be2
Revises: 21934d5ad1bb
Create Date: 2026-08-20 16:17:35.674365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7e00b1686be2'
down_revision: Union[str, Sequence[str], None] = '21934d5ad1bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу пресетов
    op.create_table('accounts_user_list_presets',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='Пользователь'),
    sa.Column('table_id', sa.String(length=50), nullable=False, comment='Идентификатор сущности (entity_key)'),
    sa.Column('name', sa.String(length=255), nullable=False, comment='Название пресета'),
    sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='Конфигурация пресета'),
    sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false', comment='Пресет по умолчанию'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='ID записи'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='Активна'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Создана'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Обновлена'),
    sa.Column('created_by_id', sa.Integer(), nullable=True, comment='Создал (user ID)'),
    sa.Column('updated_by_id', sa.Integer(), nullable=True, comment='Изменил (user ID)'),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False, comment='Удалена (soft)'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='Удалена (когда)'),
    sa.Column('deleted_by_id', sa.Integer(), nullable=True, comment='Удалил (user ID)'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts_user.id'], ),
    sa.ForeignKeyConstraint(['deleted_by_id'], ['accounts_user.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['accounts_user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['accounts_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'table_id', 'name', name='uq_user_preset_name')
    )

    # Добавляем новые колонки с server_default
    op.add_column('accounts_user_table_settings', sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='Фильтры'))
    op.add_column('accounts_user_table_settings', sa.Column('exclude_filters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='Исключения фильтров'))
    op.add_column('accounts_user_table_settings', sa.Column('sort', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Сортировка (column, direction)'))
    op.add_column('accounts_user_table_settings', sa.Column('quick_filters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]', comment='Быстрые фильтры'))

    # Обновляем комментарии
    op.alter_column('accounts_user_table_settings', 'table_id',
               existing_type=sa.VARCHAR(length=50),
               comment='Идентификатор сущности (entity_key)',
               existing_comment='Идентификатор таблицы',
               existing_nullable=False)
    op.alter_column('accounts_user_table_settings', 'column_widths',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               comment='Ширины колонок',
               existing_comment='Ширина колонок',
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('accounts_user_table_settings', 'column_widths',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               comment='Ширина колонок',
               existing_comment='Ширины колонок',
               existing_nullable=False)
    op.alter_column('accounts_user_table_settings', 'table_id',
               existing_type=sa.VARCHAR(length=50),
               comment='Идентификатор таблицы',
               existing_comment='Идентификатор сущности (entity_key)',
               existing_nullable=False)
    op.drop_column('accounts_user_table_settings', 'quick_filters')
    op.drop_column('accounts_user_table_settings', 'sort')
    op.drop_column('accounts_user_table_settings', 'exclude_filters')
    op.drop_column('accounts_user_table_settings', 'filters')
    op.drop_table('accounts_user_list_presets')
