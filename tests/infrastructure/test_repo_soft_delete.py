"""Soft-delete в BaseRepository."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.parties.models.counterparty import Depositor
from app.parties.models.legal_entity import LegalEntity
from app.parties.repository import DepositorRepository


@pytest.mark.asyncio
async def test_base_repo_hides_soft_deleted(session: AsyncSession):
    import os

    suffix = os.urandom(3).hex()
    legal = LegalEntity(name=f"LE-sd-{suffix}")
    session.add(legal)
    await session.flush()
    dep = Depositor(legal_entity_id=legal.id, code=f"SD-{suffix}")
    session.add(dep)
    await session.flush()
    dep_id = dep.id

    repo = DepositorRepository(session)
    assert await repo.get_by_id(dep_id) is not None

    await repo.soft_delete(dep_id)
    assert await repo.get_by_id(dep_id) is None
    assert await repo.get_by_id(dep_id, include_deleted=True) is not None

    alive = await repo.list_all()
    assert all(r.id != dep_id for r in alive)
