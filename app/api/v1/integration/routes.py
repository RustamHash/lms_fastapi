"""API для модуля integration."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.integration import schemas
from app.core.dependencies import get_current_user_id, get_session
from app.integration.models import (
    IntegrationError,
    IntegrationLog,
    IntegrationProfile,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]


# ========== Профили ==========

@router.get("/profiles", response_model=list[schemas.IntegrationProfileRead])
async def list_profiles(session: SessionDep) -> list[schemas.IntegrationProfileRead]:
    rows = list(await session.scalars(
        select(IntegrationProfile).where(IntegrationProfile.is_deleted.is_(False))
    ))
    return [schemas.IntegrationProfileRead.model_validate(r) for r in rows]


@router.get("/profiles/{profile_id}", response_model=schemas.IntegrationProfileRead)
async def get_profile(profile_id: int, session: SessionDep) -> schemas.IntegrationProfileRead:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Профиль не найден")
    return schemas.IntegrationProfileRead.model_validate(profile)


@router.post("/profiles", response_model=schemas.IntegrationProfileRead, status_code=status.HTTP_201_CREATED)
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


@router.patch("/profiles/{profile_id}", response_model=schemas.IntegrationProfileRead)
async def update_profile(
    profile_id: int,
    body: schemas.IntegrationProfileCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.IntegrationProfileRead:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Профиль не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    profile.updated_by_id = user_id
    await session.flush()
    return schemas.IntegrationProfileRead.model_validate(profile)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, session: SessionDep, user_id: UserDep) -> None:
    profile = await session.get(IntegrationProfile, profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Профиль не найден")
    profile.soft_delete(user_id)
    await session.flush()


# ========== Логи ==========

@router.get("/logs", response_model=list[schemas.IntegrationLogRead])
async def list_logs(
    session: SessionDep,
    profile_id: int | None = None,
) -> list[schemas.IntegrationLogRead]:
    stmt = select(IntegrationLog).where(IntegrationLog.is_deleted.is_(False))
    if profile_id:
        stmt = stmt.where(IntegrationLog.profile_id == profile_id)
    rows = list(await session.scalars(stmt))
    return [schemas.IntegrationLogRead.model_validate(r) for r in rows]


@router.get("/logs/{log_id}", response_model=schemas.IntegrationLogRead)
async def get_log(log_id: int, session: SessionDep) -> schemas.IntegrationLogRead:
    log = await session.get(IntegrationLog, log_id)
    if log is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Журнал не найден")
    return schemas.IntegrationLogRead.model_validate(log)


# ========== Ошибки ==========

@router.get("/logs/{log_id}/errors", response_model=list[schemas.IntegrationErrorRead])
async def list_errors(log_id: int, session: SessionDep) -> list[schemas.IntegrationErrorRead]:
    rows = list(await session.scalars(
        select(IntegrationError).where(IntegrationError.log_id == log_id)
    ))
    return [schemas.IntegrationErrorRead.model_validate(r) for r in rows]
