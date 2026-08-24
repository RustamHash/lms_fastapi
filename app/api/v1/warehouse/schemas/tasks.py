"""Схемы для заданий."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import TaskStatus


class TaskRead(BaseRead):
    task_type: str = Field(..., title="Тип задания")
    document_id: int | None = Field(
        None,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
    assignee_id: int | None = Field(None, title="Исполнитель")
    status: str = Field(TaskStatus.NEW.value, title="Статус")


class TaskCreate(BaseModel):
    task_type: str = Field(..., title="Тип задания")
    document_id: int | None = Field(
        None,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
    assignee_id: int | None = Field(None, title="Исполнитель")


class TaskLineAdd(BaseModel):
    task_id: int = Field(..., title="Задание")
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    plan_qty: int = Field(0, title="План")
    from_location_id: int | None = Field(None, title="Откуда")
    to_location_id: int | None = Field(None, title="Куда")
    lpn_id: int | None = Field(None, title="LPN")
    batch_id: int | None = Field(None, title="Партия")


class PickingTaskCreate(BaseModel):
    document_id: int = Field(
        ...,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
    assignee_id: int | None = Field(None, title="Исполнитель")
    warehouse_id: int = Field(
        ...,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )


class TaskUpdate(BaseModel):
    task_type: str | None = Field(None, title="Тип задания")
    document_id: int | None = Field(None, title="Документ")
    assignee_id: int | None = Field(None, title="Исполнитель")
    status: str | None = Field(None, title="Статус")


class TaskComplete(BaseModel):
    force: bool = Field(False, title="Принудительно")


class TaskLineComplete(BaseModel):
    fact_qty: int = Field(..., title="Факт")
    location_id: int | None = Field(None, title="Ячейка")
    to_location_id: int | None = Field(None, title="Куда")
    batch_id: int | None = Field(None, title="Партия")


class TaskList(BaseRead):
    task_type: str = Field(..., title="Тип задания")
    status: str = Field("new", title="Статус")
    status_label: str = Field("", title="Статус (текст)")
    assignee_id: int | None = Field(None, title="Исполнитель")
    document_number: str | None = Field(None, title="Номер документа")
    assignee_name: str | None = Field(None, title="Исполнитель")
    warehouse_name: str | None = Field(None, title="Склад")


class TaskDetail(BaseRead):
    task_type: str = Field(..., title="Тип задания")
    status: str = Field("new", title="Статус")
    assignee_id: int | None = Field(None, title="Исполнитель")
    warehouse_id: int | None = Field(None, title="Склад")
    document_number: str | None = Field(None, title="Номер документа")
    assignee_name: str | None = Field(None, title="Исполнитель")
    warehouse_name: str | None = Field(None, title="Склад")
