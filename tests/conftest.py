"""Фикстуры: реальный PostgreSQL, не sqlite."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from decimal import Decimal
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT = Path(__file__).resolve().parents[1]

import app.accounts.models  # noqa: F401
import app.delivery.models  # noqa: F401
import app.documents.models  # noqa: F401
import app.files  # noqa: F401
import app.integration.models  # noqa: F401
import app.notifications.models  # noqa: F401
import app.orders.models  # noqa: F401
import app.parties.models  # noqa: F401
import app.warehouse.models  # noqa: F401


def _base_database_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if url:
        return url
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip()
    return "postgresql+asyncpg://lms_user:lms_password@localhost:5432/lms_fastapi"


def _test_database_url() -> str:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    url = make_url(_base_database_url())
    return url.set(database="lms_fastapi_test").render_as_string(hide_password=False)


async def _ensure_database(test_database_url: str) -> None:
    admin_url = make_url(test_database_url).set(database="postgres")
    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
    )
    db_name = make_url(test_database_url).database
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :n"),
                {"n": db_name},
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await admin_engine.dispose()


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = _test_database_url()
    try:
        asyncio.run(_ensure_database(url))
    except Exception as exc:
        pytest.skip(f"PostgreSQL недоступен: {exc}")
    env = {**os.environ, "DATABASE_URL": url}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"alembic upgrade не удался:\n{result.stderr}\n{result.stdout}")
    return url


@pytest_asyncio.fixture
async def session_factory(test_database_url: str) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(test_database_url, pool_size=5, max_overflow=5)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def stock_ctx(session: AsyncSession) -> dict:
    from app.accounts.models import User
    from app.parties.models.counterparty import Depositor
    from app.parties.models.legal_entity import LegalEntity
    from app.warehouse.models import Batch, LPN, Location, Product, Row, Warehouse, Zone

    suffix = os.urandom(4).hex()
    legal = LegalEntity(name=f"LE-{suffix}")
    session.add(legal)
    await session.flush()
    depositor = Depositor(legal_entity_id=legal.id, code=f"D-{suffix}")
    session.add(depositor)
    await session.flush()

    warehouse = Warehouse(name=f"WH-{suffix}")
    session.add(warehouse)
    await session.flush()
    zone = Zone(warehouse_id=warehouse.id, name=f"Z-{suffix}", zone_type="storage")
    session.add(zone)
    await session.flush()
    row = Row(zone_id=zone.id, code="A", row_type="rack")
    session.add(row)
    await session.flush()
    loc_a = Location(row_id=row.id, position=1, level=1)
    loc_b = Location(row_id=row.id, position=2, level=1)
    session.add_all([loc_a, loc_b])
    await session.flush()

    product = Product(
        depositor_id=depositor.id,
        external_id=f"SKU-{suffix}",
        sku=f"SKU-{suffix}",
        name=f"Товар {suffix}",
        weight=Decimal("1"),
        volume=Decimal("1"),
    )
    session.add(product)
    await session.flush()
    batch = Batch(product_id=product.id, batch_number=f"B-{suffix}")
    lpn_a = LPN(number=f"P1{suffix}"[:20], status="created")
    lpn_b = LPN(number=f"P2{suffix}"[:20], status="created")
    user = User(
        username=f"u-{suffix}",
        password_hash="x",
        extra_permissions={},
    )
    session.add_all([batch, lpn_a, lpn_b, user])
    await session.flush()

    return {
        "user_id": user.id,
        "product_id": product.id,
        "location_id": loc_a.id,
        "location_b_id": loc_b.id,
        "batch_id": batch.id,
        "lpn_id": lpn_a.id,
        "lpn_b_id": lpn_b.id,
        "warehouse_id": warehouse.id,
        "depositor_id": depositor.id,
    }
