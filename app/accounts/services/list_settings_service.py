"""Сервис настроек списков и пресетов."""

from __future__ import annotations

from app.accounts.models import UserListPreset, UserTableSettings
from app.accounts.repository_list import ListPresetRepository, TableSettingsRepository
from app.core.list_defaults import get_default_prefs, merge_with_defaults


class ListSettingsService:
    def __init__(
        self,
        settings_repo: TableSettingsRepository,
        preset_repo: ListPresetRepository,
    ) -> None:
        self._settings = settings_repo
        self._presets = preset_repo

    async def get_settings(self, user_id: int, entity_key: str) -> dict:
        """Получить настройки пользователя или заводские."""
        settings = await self._settings.get_by_user_and_table(user_id, entity_key)
        if settings is None:
            return get_default_prefs(entity_key)

        return merge_with_defaults(self._to_prefs(settings), entity_key)

    async def get_defaults(self, entity_key: str) -> dict:
        """Получить заводские настройки."""
        return get_default_prefs(entity_key)

    async def save_settings(self, user_id: int, entity_key: str, prefs: dict) -> dict:
        """Сохранить настройки пользователя."""
        fields = self._from_prefs(prefs)
        settings = await self._settings.update(user_id, entity_key, **fields)
        if settings is None:
            settings = await self._settings.create(user_id, entity_key, **fields)
        return self._to_prefs(settings)

    async def delete_settings(self, user_id: int, entity_key: str) -> bool:
        """Удалить настройки пользователя."""
        return await self._settings.delete(user_id, entity_key)

    async def list_presets(self, user_id: int, entity_key: str) -> list[UserListPreset]:
        """Список пресетов."""
        return await self._presets.list_by_user_and_table(user_id, entity_key)

    async def create_preset(
        self, user_id: int, entity_key: str, name: str, config: dict, is_default: bool
    ) -> UserListPreset:
        """Создать пресет."""
        if is_default:
            await self._presets.clear_default(user_id, entity_key)
        return await self._presets.create(
            user_id=user_id,
            table_id=entity_key,
            name=name,
            config=config,
            is_default=is_default,
        )

    async def update_preset(
        self, preset_id: int, user_id: int, entity_key: str, **fields
    ) -> UserListPreset | None:
        """Обновить пресет."""
        if fields.get("is_default"):
            await self._presets.clear_default(user_id, entity_key)
        return await self._presets.update(preset_id, **fields)

    async def delete_preset(self, preset_id: int) -> bool:
        """Удалить пресет."""
        return await self._presets.delete(preset_id)

    async def apply_preset(self, user_id: int, entity_key: str, preset_id: int) -> dict:
        """Применить пресет как текущие настройки."""
        preset = await self._presets.get_by_id(preset_id)
        if preset is None:
            raise ValueError("Пресет не найден")
        return await self.save_settings(user_id, entity_key, preset.config)

    async def set_default(self, user_id: int, entity_key: str, preset_id: int) -> UserListPreset | None:
        """Установить пресет по умолчанию."""
        preset = await self._presets.get_by_id(preset_id)
        if preset is None:
            return None
        await self._presets.clear_default(user_id, entity_key)
        return await self._presets.update(preset_id, is_default=True)

    def _to_prefs(self, settings: UserTableSettings) -> dict:
        """Модель → prefs dict."""
        return {
            "order": settings.columns_order or [],
            "hidden": settings.hidden_columns or [],
            "widths": settings.column_widths or {},
            "filters": settings.filters or {},
            "exclude_filters": settings.exclude_filters or {},
            "sort": settings.sort,
            "quick_filters": settings.quick_filters or [],
        }

    def _from_prefs(self, prefs: dict) -> dict:
        """prefs dict → поля модели."""
        return {
            "columns_order": prefs.get("order", []),
            "hidden_columns": prefs.get("hidden", []),
            "column_widths": prefs.get("widths", {}),
            "filters": prefs.get("filters", {}),
            "exclude_filters": prefs.get("exclude_filters", {}),
            "sort": prefs.get("sort"),
            "quick_filters": prefs.get("quick_filters", []),
        }
