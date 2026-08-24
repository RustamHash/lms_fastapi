"""API для настроек списков и пресетов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.accounts.repository import ListPresetRepository, UserTableSettingsRepository
from app.accounts.services.list_settings_service import ListSettingsService
from app.api.deps import Services, UserDep
from app.api.v1.accounts.schemas_list import (
    PresetCreate,
    PresetRead,
    PresetUpdate,
    TableSettingsRead,
    TableSettingsUpdate,
)
from app.core.exceptions import NotFoundError, UnauthorizedError

router = APIRouter(tags=["list-settings"])


def get_service(services: Services) -> ListSettingsService:
    return ListSettingsService(
        UserTableSettingsRepository(services.session),
        ListPresetRepository(services.session),
    )


@router.get("/table-settings/{entity_key}", response_model=TableSettingsRead)
async def get_table_settings(entity_key: str, services: Services, user_id: UserDep) -> TableSettingsRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    prefs = await service.get_settings(user_id, entity_key)
    return TableSettingsRead(prefs=prefs)


@router.get("/table-settings/{entity_key}/defaults", response_model=TableSettingsRead)
async def get_table_settings_defaults(entity_key: str, services: Services) -> TableSettingsRead:
    service = get_service(services)
    prefs = service.get_defaults(entity_key)
    return TableSettingsRead(prefs=prefs)


@router.put("/table-settings/{entity_key}", response_model=TableSettingsRead)
async def put_table_settings(entity_key: str, body: TableSettingsUpdate, services: Services, user_id: UserDep) -> TableSettingsRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    prefs = await service.save_settings(user_id, entity_key, body.prefs.model_dump())
    return TableSettingsRead(prefs=prefs)


@router.delete("/table-settings/{entity_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table_settings(entity_key: str, services: Services, user_id: UserDep) -> None:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    await service.delete_settings(user_id, entity_key)


@router.get("/list-presets/{entity_key}", response_model=list[PresetRead])
async def list_presets(entity_key: str, services: Services, user_id: UserDep) -> list[PresetRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    presets = await service.list_presets(user_id, entity_key)
    return [PresetRead.model_validate(p) for p in presets]


@router.post("/list-presets/{entity_key}", response_model=PresetRead, status_code=status.HTTP_201_CREATED)
async def create_preset(entity_key: str, body: PresetCreate, services: Services, user_id: UserDep) -> PresetRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    preset = await service.create_preset(user_id, entity_key, body.name, body.config, body.is_default)
    return PresetRead.model_validate(preset)


@router.put("/list-presets/{entity_key}/{preset_id}", response_model=PresetRead)
async def update_preset(entity_key: str, preset_id: int, body: PresetUpdate, services: Services, user_id: UserDep) -> PresetRead:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    preset = await service.update_preset(preset_id, user_id, entity_key, **body.model_dump(exclude_unset=True))
    if preset is None:
        raise NotFoundError("Пресет не найден")
    return PresetRead.model_validate(preset)


@router.delete("/list-presets/{entity_key}/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(entity_key: str, preset_id: int, services: Services, user_id: UserDep) -> None:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = get_service(services)
    ok = await service.delete_preset(preset_id)
    if not ok:
        raise NotFoundError("Пресет не найден")
