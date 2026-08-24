"""API для заданий."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.warehouse.schemas import (
    PickingTaskCreate,
    TaskComplete,
    TaskCreate,
    TaskList,
    TaskRead,
    TaskUpdate,
)
from app.core.exceptions import BadRequestError, NotFoundError

router = APIRouter(prefix="/warehouse", tags=["warehouse-tasks"])


@router.get("/tasks/list", response_model=list[TaskList], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks_for_table(services: Services) -> list[TaskList]:
    rows = await services.task.list_all()
    return [TaskList.model_validate(r) for r in rows]


@router.get("/tasks", response_model=list[TaskRead], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks(services: Services) -> list[TaskRead]:
    rows = await services.task.list_all()
    return [TaskRead.model_validate(r) for r in rows]


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tasks"))])
async def create_task(body: TaskCreate, services: Services, user_id: UserDep) -> TaskRead:
    task = await services.task.create(user_id=user_id, **body.model_dump())
    return TaskRead.model_validate(task)


@router.post("/tasks/from-document", response_model=TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tasks"))])
async def create_task_from_document(body: PickingTaskCreate, services: Services, user_id: UserDep) -> TaskRead:
    task = await services.task.create(user_id=user_id, task_type="picking", document_id=body.document_id, assignee_id=body.assignee_id)
    return TaskRead.model_validate(task)


@router.get("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_permission("view", "tasks"))])
async def get_task(task_id: int, services: Services) -> TaskRead:
    task = await services.task.get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_permission("update", "tasks"))])
async def update_task(task_id: int, body: TaskUpdate, services: Services, user_id: UserDep) -> TaskRead:
    task = await services.task.update(task_id, user_id=user_id, **body.model_dump(exclude_unset=True))
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tasks"))])
async def delete_task(task_id: int, services: Services, user_id: UserDep) -> None:
    ok = await services.task.soft_delete(task_id, user_id)
    if not ok:
        raise NotFoundError("Задание не найдено")


@router.post("/tasks/{task_id}/start", response_model=TaskRead, dependencies=[Depends(require_permission("execute", "tasks"))])
async def start_task(task_id: int, services: Services, user_id: UserDep) -> TaskRead:
    task = await services.task.start(user_id=user_id, task_id=task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return TaskRead.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskRead, dependencies=[Depends(require_permission("complete", "tasks"))])
async def complete_task(task_id: int, body: TaskComplete, services: Services, user_id: UserDep) -> TaskRead:
    try:
        task = await services.task.complete(user_id=user_id, task_id=task_id, force=body.force)
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return TaskRead.model_validate(task)
