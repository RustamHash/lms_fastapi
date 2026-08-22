"""API для настроек списков и пресетов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.accounts.repository_list import ListPresetRepository, TableSettingsRepository
from app.accounts.services.list_settings_service import ListSettingsService
from app.api.deps import SessionDep, UserDep
from app.api.v1.accounts.schemas_list import (
    PresetCreate,
    PresetRead,
    PresetUpdate,
    TableSettingsRead,
    TableSettingsUpdate,
)
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError

router = APIRouter(tags=["list-settings"])


def get_service(session: SessionDep) -> ListSettingsService:
    return ListSettingsService(
        TableSettingsRepository(session),
        ListPresetRepository(session),
    )


# ========== Настройки ==========

@router.post("/table-settings/{entity_key}", response_model=TableSettingsRead, status_code=status.HTTP_201_CREATED)
async def create_table_settings(
    entity_key: str,
    body: TableSettingsUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> TableSettingsRead:
    """Создать настройки таблицы."""
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    prefs = await service.save_settings(user_id, entity_key, body.prefs.model_dump())
    return TableSettingsRead(prefs=prefs)


@router.get("/table-settings/{entity_key}", response_model=TableSettingsRead)
async def get_table_settings(
    entity_key: str,
    session: SessionDep,
    user_id: UserDep,
) -> TableSettingsRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    prefs = await service.get_settings(user_id, entity_key)
    return TableSettingsRead(prefs=prefs)


@router.get("/table-settings/{entity_key}/defaults", response_model=TableSettingsRead)
async def get_table_settings_defaults(
    entity_key: str,
) -> TableSettingsRead:
    service = get_service(None)
    prefs = service.get_defaults(entity_key)
    return TableSettingsRead(prefs=prefs)


@router.put("/table-settings/{entity_key}", response_model=TableSettingsRead)
async def put_table_settings(
    entity_key: str,
    body: TableSettingsUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> TableSettingsRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    prefs = await service.save_settings(user_id, entity_key, body.prefs.model_dump())
    return TableSettingsRead(prefs=prefs)


@router.delete("/table-settings/{entity_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table_settings(
    entity_key: str,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    await service.delete_settings(user_id, entity_key)


# ========== Пресеты ==========

@router.get("/list-presets/{entity_key}", response_model=list[PresetRead])
async def list_presets(
    entity_key: str,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    presets = await service.list_presets(user_id, entity_key)
    return [PresetRead.model_validate(p) for p in presets]


@router.post("/list-presets/{entity_key}", status_code=status.HTTP_201_CREATED)
async def create_preset(
    entity_key: str,
    body: PresetCreate,
    session: SessionDep,
    user_id: UserDep,
) -> PresetRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    preset = await service.create_preset(
        user_id, entity_key, body.name, body.config, body.is_default
    )
    return PresetRead.model_validate(preset)


@router.put("/list-presets/{entity_key}/{preset_id}")
async def update_preset(
    entity_key: str,
    preset_id: int,
    body: PresetUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> PresetRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    preset = await service.update_preset(
        preset_id, user_id, entity_key, **body.model_dump(exclude_unset=True)
    )
    if preset is None:
        raise NotFoundError("Пресет не найден")
    return PresetRead.model_validate(preset)


@router.delete("/list-presets/{entity_key}/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    entity_key: str,
    preset_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    ok = await service.delete_preset(preset_id)
    if not ok:
        raise NotFoundError("Пресет не найден")


@router.post("/list-presets/{entity_key}/{preset_id}/apply")
async def apply_preset(
    entity_key: str,
    preset_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> TableSettingsRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    try:
        prefs = await service.apply_preset(user_id, entity_key, preset_id)
    except ValueError as e:
        raise NotFoundError(str(e)) from e
    return TableSettingsRead(prefs=prefs)


@router.post("/list-presets/{entity_key}/{preset_id}/set-default")
async def set_default_preset(
    entity_key: str,
    preset_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> PresetRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(session)
    preset = await service.set_default(user_id, entity_key, preset_id)
    if preset is None:
        raise NotFoundError("Пресет не найден")
    return PresetRead.model_validate(preset)
