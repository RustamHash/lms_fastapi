"""accounts rbac: drop parent_role, cascade FKs, partial uniques

Revision ID: 20260825014300
Revises: 20260822160522
Create Date: 2026-08-25 01:43:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260825014300"
down_revision = "20260822160522"
branch_labels = None
depends_on = None


def _fk_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {fk["name"] for fk in inspector.get_foreign_keys(table) if fk["name"]}


def _uq_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {uc["name"] for uc in inspector.get_unique_constraints(table) if uc["name"]}


def _index_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {ix["name"] for ix in inspector.get_indexes(table) if ix["name"]}


def _drop_fk(table: str, name: str) -> None:
    if name in _fk_names(table):
        op.drop_constraint(name, table, type_="foreignkey")


def _drop_uq(table: str, name: str) -> None:
    if name in _uq_names(table):
        op.drop_constraint(name, table, type_="unique")


def _drop_index(table: str, name: str) -> None:
    if name in _index_names(table):
        op.drop_index(name, table_name=table)


def upgrade() -> None:
    # Partial unique on accounts_role.code is illegal while this FK exists.
    _drop_fk("notifications_rule", "notifications_rule_role_code_fkey")

    _drop_fk("accounts_role", "accounts_role_parent_role_id_fkey")
    columns = {col["name"] for col in sa.inspect(op.get_bind()).get_columns("accounts_role")}
    if "parent_role_id" in columns:
        op.drop_column("accounts_role", "parent_role_id")

    _drop_fk("accounts_user_roles", "accounts_user_roles_user_id_fkey")
    _drop_fk("accounts_user_roles", "accounts_user_roles_role_id_fkey")
    op.create_foreign_key(
        "accounts_user_roles_user_id_fkey",
        "accounts_user_roles",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "accounts_user_roles_role_id_fkey",
        "accounts_user_roles",
        "accounts_role",
        ["role_id"],
        ["id"],
        ondelete="CASCADE",
    )

    _drop_fk("accounts_user_depositor", "accounts_user_depositor_user_id_fkey")
    _drop_fk("accounts_user_depositor", "accounts_user_depositor_depositor_id_fkey")
    op.create_foreign_key(
        "accounts_user_depositor_user_id_fkey",
        "accounts_user_depositor",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "accounts_user_depositor_depositor_id_fkey",
        "accounts_user_depositor",
        "parties_depositor",
        ["depositor_id"],
        ["id"],
        ondelete="CASCADE",
    )

    _drop_index("accounts_user", "ix_accounts_user_username")
    op.create_index("ix_accounts_user_username", "accounts_user", ["username"], unique=False)
    op.create_index(
        "uq_accounts_user_username_alive",
        "accounts_user",
        ["username"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )

    op.execute("UPDATE accounts_user SET email = NULL WHERE email = ''")
    op.alter_column(
        "accounts_user",
        "email",
        existing_type=sa.String(length=255),
        nullable=True,
        comment="Email",
    )
    op.create_index(
        "uq_accounts_user_email_alive",
        "accounts_user",
        ["email"],
        unique=True,
        postgresql_where=sa.text("email IS NOT NULL AND is_deleted = false"),
    )

    _drop_uq("accounts_role", "accounts_role_code_key")
    _drop_uq("accounts_role", "accounts_role_name_key")
    _drop_index("accounts_role", "ix_accounts_role_code")
    _drop_index("accounts_role", "ix_accounts_role_name")
    op.create_index(
        "uq_accounts_role_code_alive",
        "accounts_role",
        ["code"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )
    op.create_index(
        "uq_accounts_role_name_alive",
        "accounts_role",
        ["name"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    _drop_index("accounts_role", "uq_accounts_role_name_alive")
    _drop_index("accounts_role", "uq_accounts_role_code_alive")
    op.create_unique_constraint("accounts_role_code_key", "accounts_role", ["code"])
    op.create_unique_constraint("accounts_role_name_key", "accounts_role", ["name"])

    _drop_index("accounts_user", "uq_accounts_user_email_alive")
    op.execute("UPDATE accounts_user SET email = '' WHERE email IS NULL")
    op.alter_column(
        "accounts_user",
        "email",
        existing_type=sa.String(length=255),
        nullable=False,
        comment="Email",
    )

    _drop_index("accounts_user", "uq_accounts_user_username_alive")
    _drop_index("accounts_user", "ix_accounts_user_username")
    op.create_index("ix_accounts_user_username", "accounts_user", ["username"], unique=True)

    _drop_fk("accounts_user_depositor", "accounts_user_depositor_user_id_fkey")
    _drop_fk("accounts_user_depositor", "accounts_user_depositor_depositor_id_fkey")
    op.create_foreign_key(
        "accounts_user_depositor_user_id_fkey",
        "accounts_user_depositor",
        "accounts_user",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "accounts_user_depositor_depositor_id_fkey",
        "accounts_user_depositor",
        "parties_depositor",
        ["depositor_id"],
        ["id"],
    )

    _drop_fk("accounts_user_roles", "accounts_user_roles_user_id_fkey")
    _drop_fk("accounts_user_roles", "accounts_user_roles_role_id_fkey")
    op.create_foreign_key(
        "accounts_user_roles_user_id_fkey",
        "accounts_user_roles",
        "accounts_user",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "accounts_user_roles_role_id_fkey",
        "accounts_user_roles",
        "accounts_role",
        ["role_id"],
        ["id"],
    )

    op.add_column(
        "accounts_role",
        sa.Column("parent_role_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "accounts_role_parent_role_id_fkey",
        "accounts_role",
        "accounts_role",
        ["parent_role_id"],
        ["id"],
    )

    op.create_foreign_key(
        "notifications_rule_role_code_fkey",
        "notifications_rule",
        "accounts_role",
        ["role_code"],
        ["code"],
    )
