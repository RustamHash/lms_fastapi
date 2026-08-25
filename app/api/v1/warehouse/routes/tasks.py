"""API для заданий."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import get_task_service
from app.api.v1.warehouse.schemas import (
    PickingTaskCreate,
    TaskComplete,
    TaskCreate,
    TaskList,
    TaskRead,
    TaskUpdate,
)
from app.core.exceptions import BadRequestError, NotFoundError
from app.warehouse.services.task_service import TaskService

router = APIRouter(prefix="/warehouse", tags=["warehouse-tasks"])


@router.get("/tasks/list", response_model=list[TaskList], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks_for_table(service: TaskService = Depends(get_task_service)) -> list[TaskList]:
    rows = await service.list_all()
    return [TaskList.model_validate(r) for r in rows]


@router.get("/tasks", response_model=list[TaskRead], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks(service: TaskService = Depends(get_task_service)) -> list[TaskRead]:
    rows = await service.list_all()
    return [TaskRead.model_validate(r) for r in rows]


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tasks"))])
async def create_task(
    body: TaskCreate,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.create(user_id=user_id, **body.model_dump())
    return TaskRead.model_validate(task)


@router.post("/tasks/from-document", response_model=TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tasks"))])
async def create_task_from_document(
    body: PickingTaskCreate,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.create(
        user_id=user_id,
        task_type="picking",
        document_id=body.document_id,
        assignee_id=body.assignee_id,
    )
    return TaskRead.model_validate(task)


@router.get("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_permission("view", "tasks"))])
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_permission("update", "tasks"))])
async def update_task(
    task_id: int,
    body: TaskUpdate,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.update(task_id, user_id=user_id, **body.model_dump(exclude_unset=True))
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tasks"))])
async def delete_task(
    task_id: int,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> None:
    ok = await service.soft_delete(task_id, user_id)
    if not ok:
        raise NotFoundError("Задание не найдено")


@router.post("/tasks/{task_id}/start", response_model=TaskRead, dependencies=[Depends(require_permission("execute", "tasks"))])
async def start_task(
    task_id: int,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.start(user_id=user_id, task_id=task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskRead, dependencies=[Depends(require_permission("complete", "tasks"))])
async def complete_task(
    task_id: int,
    body: TaskComplete,
    user_id: UserDep,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    try:
        task = await service.complete(user_id=user_id, task_id=task_id, force=body.force)
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return TaskRead.model_validate(task)
