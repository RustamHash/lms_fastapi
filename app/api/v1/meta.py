"""API для метаданных сущностей (поля, типы, label)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.v1.parties.schemas import (
    AddressRead,
    CarrierRead,
    ClientRead,
    ContractRead,
    DeliveryZoneRead,
    DepositorRead,
    KeeperRead,
    LegalEntityRead,
    RawAddressRead,
    TariffDocumentRead,
    TariffRead,
)
from app.api.v1.warehouse.schemas import (
    BatchRead,
    LPNRead,
    LocationRead,
    ProductRead,
    RowRead,
    StockBalanceRead,
    TaskList,
    VirtualWarehouseRead,
    WarehouseRead,
    ZoneRead,
)
from app.api.v1.orders.schemas import (
    InboundOrderRead,
    OutboundOrderRead,
    ReturnOrderRead,
)
from app.api.v1.delivery.schemas import (
    DeliveryOrderRead,
    DriverRead,
    RouteRead,
    VehicleRead,
)
from app.api.v1.documents.schemas import DocumentRead
from app.api.v1.notifications.schemas import NotificationRead
from app.api.v1.integration.schemas import IntegrationProfileRead

router = APIRouter(prefix="/entities", tags=["meta"])

MODEL_MAP: dict[str, type] = {
    "addresses": AddressRead,
    "carriers": CarrierRead,
    "clients": ClientRead,
    "contracts": ContractRead,
    "delivery_zones": DeliveryZoneRead,
    "depositors": DepositorRead,
    "keepers": KeeperRead,
    "legal_entities": LegalEntityRead,
    "aliases": RawAddressRead,
    "tariff_documents": TariffDocumentRead,
    "tariffs": TariffRead,
    "batches": BatchRead,
    "lpns": LPNRead,
    "locations": LocationRead,
    "products": ProductRead,
    "rows": RowRead,
    "stock_balances": StockBalanceRead,
    "tasks": TaskList,
    "virtual_warehouses": VirtualWarehouseRead,
    "warehouses": WarehouseRead,
    "zones": ZoneRead,
    "inbound_orders": InboundOrderRead,
    "outbound_orders": OutboundOrderRead,
    "return_orders": ReturnOrderRead,
    "delivery_orders": DeliveryOrderRead,
    "drivers": DriverRead,
    "routes": RouteRead,
    "vehicles": VehicleRead,
    "documents": DocumentRead,
    "notifications": NotificationRead,
    "integration_profiles": IntegrationProfileRead,
}

# Ключи, которые нужно прокидывать через $ref
_EXTRA_KEYS = ("ui_type", "endpoint", "label_field", "value_field")


def _resolve_ref(ref: str, definitions: dict) -> dict:
    """Резолвит $ref ссылку."""
    name = ref.split("/")[-1]
    return dict(definitions.get(name, {}))


def _unwrap_field(field_info: dict, definitions: dict) -> dict:
    """
    Раскрывает $ref и anyOf, сохраняя:
    - title из оригинального поля
    - ui_type, endpoint, label_field, value_field
    """
    original_title = field_info.get("title")
    original_extra = {
        k: v for k, v in field_info.items() if k in _EXTRA_KEYS
    }

    result = None

    # $ref
    if "$ref" in field_info:
        result = _resolve_ref(field_info["$ref"], definitions)

    # anyOf — первый не-null вариант
    elif "anyOf" in field_info:
        for variant in field_info["anyOf"]:
            if "$ref" in variant:
                result = _resolve_ref(variant["$ref"], definitions)
                break
            if variant.get("type") != "null":
                result = dict(variant)
                break

    if result is None:
        result = dict(field_info)

    # Прокидываем title
    if original_title:
        result["title"] = original_title

    # Прокидываем extra-ключи
    for key, value in original_extra.items():
        result[key] = value

    return result


def _extract_nested(properties: dict, definitions: dict, depth: int = 0) -> dict:
    """Рекурсивно извлекает вложенные поля."""
    if depth > 5:
        return {}

    nested = {}
    for name, field_info in properties.items():
        field_info = _unwrap_field(field_info, definitions)

        field_data = {
            "title": field_info.get("title", name),
            "type": field_info.get("type", "string"),
        }

        if field_info.get("format"):
            field_data["format"] = field_info["format"]

        if "enum" in field_info:
            field_data["enum"] = field_info["enum"]

        # ui_type select
        if field_info.get("ui_type") == "select":
            field_data["type"] = "select"
            field_data["endpoint"] = field_info.get("endpoint")
            field_data["label_field"] = field_info.get("label_field", "name")
            field_data["value_field"] = field_info.get("value_field", "id")

        # Вложенный объект
        if "properties" in field_info:
            field_data["type"] = "object"
            field_data["nested"] = _extract_nested(
                field_info["properties"], definitions, depth + 1
            )

        nested[name] = field_data

    return nested


def _get_field_type(field_info: dict) -> str:
    """Определяет тип поля."""
    if field_info.get("ui_type"):
        return field_info["ui_type"]

    format_type = field_info.get("format")
    if format_type == "date-time":
        return "datetime"
    if format_type == "date":
        return "date"

    pydantic_type = field_info.get("type")
    type_map = {
        "string": "string",
        "integer": "integer",
        "number": "number",
        "boolean": "boolean",
        "array": "array",
        "object": "object",
    }
    return type_map.get(pydantic_type, pydantic_type or "string")


def _extract_fields(schema_class: type) -> dict:
    """Извлекает метаданные полей из Pydantic-схемы."""
    schema = schema_class.model_json_schema()
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    definitions = schema.get("$defs", {})

    fields = {}
    for name, field_info in properties.items():
        field_info = _unwrap_field(field_info, definitions)

        field_data = {
            "title": field_info.get("title", name),
            "type": _get_field_type(field_info),
            "required": name in required,
            "default": field_info.get("default"),
        }

        if "enum" in field_info:
            field_data["enum"] = field_info["enum"]

        if field_info.get("ui_type") == "select":
            field_data["type"] = "select"
            field_data["endpoint"] = field_info.get("endpoint")
            field_data["label_field"] = field_info.get("label_field", "name")
            field_data["value_field"] = field_info.get("value_field", "id")

        if field_info.get("format"):
            field_data["format"] = field_info["format"]

        if "properties" in field_info:
            field_data["type"] = "object"
            field_data["nested"] = _extract_nested(
                field_info["properties"], definitions
            )

        fields[name] = field_data

    return fields


@router.get("/{entity}/fields")
async def get_entity_fields(entity: str) -> dict:
    """Возвращает метаданные полей для сущности."""
    schema_class = MODEL_MAP.get(entity)
    if schema_class is None:
        raise HTTPException(status_code=404, detail=f"Сущность '{entity}' не найдена")

    return {
        "entity": entity,
        "fields": _extract_fields(schema_class),
    }


@router.get("/")
async def list_entities() -> list[str]:
    """Возвращает список всех доступных сущностей."""
    return list(MODEL_MAP.keys())
