"""API для настроек пользователя и привязок к поклажедателю."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.accounts.repository import UserDepositorRepository, UserSettingsRepository
from app.api.deps import Services, UserDep, require_permission
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(tags=["user-settings"])


class UserSettingsCreate(BaseModel):
    user_id: int = Field(..., title="Пользователь")
    menu_style: str = Field("top", title="Стиль меню")
    theme: str = Field("light", title="Тема")
    density: str = Field("compact", title="Плотность")
    font_size: str = Field("small", title="Размер шрифта")


class UserSettingsUpdate(BaseModel):
    menu_style: str | None = Field(None, title="Стиль меню")
    theme: str | None = Field(None, title="Тема")
    density: str | None = Field(None, title="Плотность")
    font_size: str | None = Field(None, title="Размер шрифта")


class UserDepositorCreate(BaseModel):
    user_id: int = Field(..., title="Пользователь")
    depositor_id: int = Field(..., title="Поклажедатель")


@router.get("/user-settings", dependencies=[Depends(require_permission("view", "users"))])
async def list_user_settings(services: Services):
    rows = await UserSettingsRepository(services.session).list_all()
    return [
        {"id": s.id, "user_id": s.user_id, "menu_style": s.menu_style, "theme": s.theme, "density": s.density, "font_size": s.font_size}
        for s in rows
    ]


@router.post("/user-settings", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user_settings(body: UserSettingsCreate, services: Services, user_id: UserDep):
    existing = await UserSettingsRepository(services.session).get_by_user(body.user_id)
    if existing:
        raise ConflictError("Настройки для пользователя уже существуют")
    settings = await UserSettingsRepository(services.session).create(**body.model_dump())
    return {"id": settings.id}


@router.get("/user-settings/{settings_id}", dependencies=[Depends(require_permission("view", "users"))])
async def get_user_settings(settings_id: int, services: Services):
    s = await UserSettingsRepository(services.session).get_by_id(settings_id)
    if s is None:
        raise NotFoundError("Настройки не найдены")
    return {"id": s.id, "user_id": s.user_id, "menu_style": s.menu_style, "theme": s.theme, "density": s.density, "font_size": s.font_size}


@router.patch("/user-settings/{settings_id}", dependencies=[Depends(require_permission("update", "users"))])
async def update_user_settings(settings_id: int, body: UserSettingsUpdate, services: Services, user_id: UserDep):
    s = await UserSettingsRepository(services.session).update(settings_id, **body.model_dump(exclude_unset=True))
    if s is None:
        raise NotFoundError("Настройки не найдены")
    return {"id": s.id}


@router.delete("/user-settings/{settings_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user_settings(settings_id: int, services: Services, user_id: UserDep):
    ok = await UserSettingsRepository(services.session).soft_delete(settings_id, user_id)
    if not ok:
        raise NotFoundError("Настройки не найдены")


@router.get("/user-depositors", dependencies=[Depends(require_permission("view", "users"))])
async def list_user_depositors(services: Services):
    rows = await UserDepositorRepository(services.session).list_all()
    return [{"id": ud.id, "user_id": ud.user_id, "depositor_id": ud.depositor_id} for ud in rows]


@router.post("/user-depositors", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user_depositor(body: UserDepositorCreate, services: Services, user_id: UserDep):
    existing = await UserDepositorRepository(services.session).get_by_user_and_depositor(body.user_id, body.depositor_id)
    if existing:
        raise ConflictError("Привязка уже существует")
    ud = await UserDepositorRepository(services.session).create(**body.model_dump())
    return {"id": ud.id}


@router.delete("/user-depositors/{ud_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user_depositor(ud_id: int, services: Services, user_id: UserDep):
    ok = await UserDepositorRepository(services.session).soft_delete(ud_id, user_id)
    if not ok:
        raise NotFoundError("Привязка не найдена")
