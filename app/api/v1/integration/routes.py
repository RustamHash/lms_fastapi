"""API для модуля integration."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.integration import schemas
from app.core.exceptions import NotFoundError
from app.integration.models import (
    IntegrationError,
    IntegrationLog,
    IntegrationProfile,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ========== Профили ==========

@router.get("/profiles", response_model=list[schemas.IntegrationProfileRead], dependencies=[Depends(require_permission("view", "integrations"))])
async def list_profiles(session: SessionDep) -> list[schemas.IntegrationProfileRead]:
    rows = list(await session.scalars(
        select(IntegrationProfile).where()
    ))
    return [schemas.IntegrationProfileRead.model_validate(r) for r in rows]


@router.get("/profiles/{profile_id}", response_model=schemas.IntegrationProfileRead, dependencies=[Depends(require_permission("view", "integrations"))])
async def get_profile(profile_id: int, session: SessionDep) -> schemas.IntegrationProfileRead:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise NotFoundError("Профиль не найден")
    return schemas.IntegrationProfileRead.model_validate(profile)


@router.post("/profiles", response_model=schemas.IntegrationProfileRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "integrations"))])
async def create_profile(
    body: schemas.IntegrationProfileCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.IntegrationProfileRead:
    profile = IntegrationProfile(
        created_by_id=user_id,
        updated_by_id=user_id,
        **body.model_dump(),
    )
    session.add(profile)
    await session.flush()
    return schemas.IntegrationProfileRead.model_validate(profile)


@router.patch("/profiles/{profile_id}", response_model=schemas.IntegrationProfileRead, dependencies=[Depends(require_permission("update", "integrations"))])
async def update_profile(
    profile_id: int,
    body: schemas.IntegrationProfileCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.IntegrationProfileRead:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise NotFoundError("Профиль не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    profile.updated_by_id = user_id
    await session.flush()
    return schemas.IntegrationProfileRead.model_validate(profile)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "integrations"))])
async def delete_profile(profile_id: int, session: SessionDep, user_id: UserDep) -> None:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise NotFoundError("Профиль не найден")
    profile.soft_delete(user_id)
    await session.flush()


# ========== Логи ==========

@router.get("/logs", response_model=list[schemas.IntegrationLogRead], dependencies=[Depends(require_permission("view", "integrations"))])
async def list_logs(
    session: SessionDep,
    profile_id: int | None = None,
) -> list[schemas.IntegrationLogRead]:
    stmt = select(IntegrationLog).where()
    if profile_id:
        stmt = stmt.where(IntegrationLog.profile_id == profile_id)
    rows = list(await session.scalars(stmt))
    return [schemas.IntegrationLogRead.model_validate(r) for r in rows]


@router.get("/logs/{log_id}", response_model=schemas.IntegrationLogRead, dependencies=[Depends(require_permission("view", "integrations"))])
async def get_log(log_id: int, session: SessionDep) -> schemas.IntegrationLogRead:
    log = await session.get(IntegrationLog, log_id)
    if log is None:
        raise NotFoundError("Журнал не найден")
    return schemas.IntegrationLogRead.model_validate(log)


# ========== Ошибки ==========

@router.get("/logs/{log_id}/errors", response_model=list[schemas.IntegrationErrorRead], dependencies=[Depends(require_permission("view", "integrations"))])
async def list_errors(log_id: int, session: SessionDep) -> list[schemas.IntegrationErrorRead]:
    rows = list(await session.scalars(
        select(IntegrationError).where(IntegrationError.log_id == log_id)
    ))
    return [schemas.IntegrationErrorRead.model_validate(r) for r in rows]
