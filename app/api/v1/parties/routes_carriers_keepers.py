"""API для перевозчиков и хранителей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.parties.schemas import (
    CarrierCreate,
    CarrierRead,
    KeeperCreate,
    KeeperRead,
)
from app.core.exceptions import ConflictError, NotFoundError
from app.parties.models import Carrier, Keeper

router = APIRouter(tags=["carriers-keepers"])


# ========== Перевозчики ==========

@router.get(
    "/carriers",
    response_model=list[CarrierRead],
    dependencies=[Depends(require_permission("view", "carriers"))],
)
async def list_carriers(session: SessionDep) -> list[CarrierRead]:
    rows = list(await session.scalars(select(Carrier)))
    return [CarrierRead.model_validate(r) for r in rows]


@router.post(
    "/carriers",
    response_model=CarrierRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "carriers"))],
)
async def create_carrier(
    body: CarrierCreate,
    session: SessionDep,
    user_id: UserDep,
) -> CarrierRead:
    existing = await session.scalar(
        select(Carrier).where(Carrier.legal_entity_id == body.legal_entity_id)
    )
    if existing:
        raise ConflictError("Перевозчик с таким юрлицом уже существует")

    carrier = Carrier(
        legal_entity_id=body.legal_entity_id,
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(carrier)
    await session.flush()
    return CarrierRead.model_validate(carrier)


@router.get(
    "/carriers/{carrier_id}",
    response_model=CarrierRead,
    dependencies=[Depends(require_permission("view", "carriers"))],
)
async def get_carrier(carrier_id: int, session: SessionDep) -> CarrierRead:
    carrier = await session.get(Carrier, carrier_id)
    if carrier is None:
        raise NotFoundError("Перевозчик не найден")
    return CarrierRead.model_validate(carrier)


@router.patch(
    "/carriers/{carrier_id}",
    response_model=CarrierRead,
    dependencies=[Depends(require_permission("update", "carriers"))],
)
async def update_carrier(
    carrier_id: int,
    body: CarrierCreate,
    session: SessionDep,
    user_id: UserDep,
) -> CarrierRead:
    carrier = await session.get(Carrier, carrier_id)
    if carrier is None:
        raise NotFoundError("Перевозчик не найден")
    carrier.legal_entity_id = body.legal_entity_id
    carrier.updated_by_id = user_id
    await session.flush()
    return CarrierRead.model_validate(carrier)


@router.delete(
    "/carriers/{carrier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "carriers"))],
)
async def delete_carrier(carrier_id: int, session: SessionDep, user_id: UserDep) -> None:
    carrier = await session.get(Carrier, carrier_id)
    if carrier is None:
        raise NotFoundError("Перевозчик не найден")
    carrier.soft_delete(user_id)
    await session.flush()


# ========== Хранители ==========

@router.get(
    "/keepers",
    response_model=list[KeeperRead],
    dependencies=[Depends(require_permission("view", "keepers"))],
)
async def list_keepers(session: SessionDep) -> list[KeeperRead]:
    rows = list(await session.scalars(select(Keeper)))
    return [KeeperRead.model_validate(r) for r in rows]


@router.post(
    "/keepers",
    response_model=KeeperRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "keepers"))],
)
async def create_keeper(
    body: KeeperCreate,
    session: SessionDep,
    user_id: UserDep,
) -> KeeperRead:
    existing = await session.scalar(
        select(Keeper).where(Keeper.legal_entity_id == body.legal_entity_id)
    )
    if existing:
        raise ConflictError("Хранитель с таким юрлицом уже существует")

    keeper = Keeper(
        legal_entity_id=body.legal_entity_id,
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(keeper)
    await session.flush()
    return KeeperRead.model_validate(keeper)


@router.get(
    "/keepers/{keeper_id}",
    response_model=KeeperRead,
    dependencies=[Depends(require_permission("view", "keepers"))],
)
async def get_keeper(keeper_id: int, session: SessionDep) -> KeeperRead:
    keeper = await session.get(Keeper, keeper_id)
    if keeper is None:
        raise NotFoundError("Хранитель не найден")
    return KeeperRead.model_validate(keeper)


@router.patch(
    "/keepers/{keeper_id}",
    response_model=KeeperRead,
    dependencies=[Depends(require_permission("update", "keepers"))],
)
async def update_keeper(
    keeper_id: int,
    body: KeeperCreate,
    session: SessionDep,
    user_id: UserDep,
) -> KeeperRead:
    keeper = await session.get(Keeper, keeper_id)
    if keeper is None:
        raise NotFoundError("Хранитель не найден")
    keeper.legal_entity_id = body.legal_entity_id
    keeper.updated_by_id = user_id
    await session.flush()
    return KeeperRead.model_validate(keeper)


@router.delete(
    "/keepers/{keeper_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "keepers"))],
)
async def delete_keeper(keeper_id: int, session: SessionDep, user_id: UserDep) -> None:
    keeper = await session.get(Keeper, keeper_id)
    if keeper is None:
        raise NotFoundError("Хранитель не найден")
    keeper.soft_delete(user_id)
    await session.flush()
