"""API для настроек пользователя и привязок к поклажедателю."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select

from app.accounts.models import UserDepositor, UserSettings
from app.accounts.repository import UserSettingsRepository, UserDepositorRepository
from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(tags=["user-settings"])


class UserSettingsCreate(BaseModel):
    user_id: int
    menu_style: str = "top"
    theme: str = "light"
    density: str = "compact"
    font_size: str = "small"


class UserSettingsUpdate(BaseModel):
    menu_style: str | None = None
    theme: str | None = None
    density: str | None = None
    font_size: str | None = None


class UserDepositorCreate(BaseModel):
    user_id: int
    depositor_id: int


class UserDepositorUpdate(BaseModel):
    user_id: int | None = None
    depositor_id: int | None = None


# ========== Настройки пользователя ==========

@router.get("/user-settings", dependencies=[Depends(require_permission("view", "users"))])
async def list_user_settings(session: SessionDep):
    rows = await UserSettingsRepository(session).list_all()
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "menu_style": s.menu_style,
            "theme": s.theme,
            "density": s.density,
            "font_size": s.font_size,
            "is_active": s.is_active,
            "is_deleted": s.is_deleted,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in rows
    ]


@router.post("/user-settings", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user_settings(body: UserSettingsCreate, session: SessionDep, user_id: UserDep):
    existing = await UserSettingsRepository(session).get_by_user(body.user_id)
    if existing:
        raise ConflictError("Настройки для пользователя уже существуют")

    settings = UserSettings(
        user_id=body.user_id,
        menu_style=body.menu_style,
        theme=body.theme,
        density=body.density,
        font_size=body.font_size,
    )
    session.add(settings)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": settings.id}


@router.get("/user-settings/{settings_id}", dependencies=[Depends(require_permission("view", "users"))])
async def get_user_settings(settings_id: int, session: SessionDep):
    s = await UserSettingsRepository(session).get_by_id(settings_id)
    if s is None:
        raise NotFoundError("Настройки не найдены")
    return {
        "id": s.id,
        "user_id": s.user_id,
        "menu_style": s.menu_style,
        "theme": s.theme,
        "density": s.density,
        "font_size": s.font_size,
        "is_active": s.is_active,
        "is_deleted": s.is_deleted,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
    }


@router.patch("/user-settings/{settings_id}", dependencies=[Depends(require_permission("update", "users"))])
async def update_user_settings(settings_id: int, body: UserSettingsUpdate, session: SessionDep, user_id: UserDep):
    s = await UserSettingsRepository(session).get_by_id(settings_id)
    if s is None:
        raise NotFoundError("Настройки не найдены")
    for field in ["menu_style", "theme", "density", "font_size"]:
        if field in body:
            setattr(s, field, body[field])
    s.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": s.id}


@router.delete("/user-settings/{settings_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user_settings(settings_id: int, session: SessionDep, user_id: UserDep):
    s = await UserSettingsRepository(session).get_by_id(settings_id)
    if s is None:
        raise NotFoundError("Настройки не найдены")
    s.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Привязки к поклажедателю ==========

@router.get("/user-depositors", dependencies=[Depends(require_permission("view", "users"))])
async def list_user_depositors(session: SessionDep, user_id: int | None = None):
    repo = UserDepositorRepository(session)
    rows = await repo.list_all()
    return [
        {
            "id": ud.id,
            "user_id": ud.user_id,
            "depositor_id": ud.depositor_id,
            "is_active": ud.is_active,
            "is_deleted": ud.is_deleted,
            "created_at": ud.created_at,
            "updated_at": ud.updated_at,
        }
        for ud in rows
    ]


@router.post("/user-depositors", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user_depositor(body: UserDepositorCreate, session: SessionDep, user_id: UserDep):
    existing = await UserDepositorRepository(session).get_by_user_and_depositor(
        body.user_id, body.depositor_id
    )
    if existing:
        raise ConflictError("Привязка уже существует")

    ud = UserDepositor(
        user_id=body.user_id,
        depositor_id=body.depositor_id,
    )
    session.add(ud)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": ud.id}


@router.get("/user-depositors/{ud_id}", dependencies=[Depends(require_permission("view", "users"))])
async def get_user_depositor(ud_id: int, session: SessionDep):
    ud = await UserDepositorRepository(session).get_by_id(ud_id)
    if ud is None:
        raise NotFoundError("Привязка не найдена")
    return {
        "id": ud.id,
        "user_id": ud.user_id,
        "depositor_id": ud.depositor_id,
        "is_active": ud.is_active,
        "is_deleted": ud.is_deleted,
        "created_at": ud.created_at,
        "updated_at": ud.updated_at,
    }


@router.patch("/user-depositors/{ud_id}", dependencies=[Depends(require_permission("update", "users"))])
async def update_user_depositor(ud_id: int, body: UserDepositorUpdate, session: SessionDep, user_id: UserDep):
    ud = await UserDepositorRepository(session).get_by_id(ud_id)
    if ud is None:
        raise NotFoundError("Привязка не найдена")
    for field in ["user_id", "depositor_id"]:
        if field in body:
            setattr(ud, field, body[field])
    ud.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": ud.id}


@router.delete("/user-depositors/{ud_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user_depositor(ud_id: int, session: SessionDep, user_id: UserDep):
    ud = await UserDepositorRepository(session).get_by_id(ud_id)
    if ud is None:
        raise NotFoundError("Привязка не найдена")
    ud.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
