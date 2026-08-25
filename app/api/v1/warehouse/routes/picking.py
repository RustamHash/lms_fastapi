"""Воркфлоу отбора."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import get_picking_service
from app.api.v1.warehouse.schemas.tasks import TaskRead
from app.api.v1.warehouse.schemas.workflow import PickLineBody, PickingFromOutbound
from app.warehouse.services.picking_service import PickingService

router = APIRouter(prefix="/warehouse/picking", tags=["warehouse-picking"])


@router.post(
    "/from-outbound",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("create", "tasks"))],
)
async def create_picking_from_outbound(
    body: PickingFromOutbound,
    user_id: UserDep,
    service: PickingService = Depends(get_picking_service),
) -> TaskRead:
    task = await service.create_from_outbound(
        user_id=user_id, outbound_order_id=body.outbound_order_id
    )
    return TaskRead.model_validate(task)


@router.post(
    "/{task_id}/plan",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("execute", "tasks"))],
)
async def plan_picking(
    task_id: int,
    user_id: UserDep,
    service: PickingService = Depends(get_picking_service),
) -> TaskRead:
    task = await service.plan_lines(user_id=user_id, task_id=task_id)
    return TaskRead.model_validate(task)


@router.post(
    "/lines/{line_id}/pick",
    dependencies=[Depends(require_permission("execute", "tasks"))],
)
async def pick_line(
    line_id: int,
    body: PickLineBody,
    user_id: UserDep,
    service: PickingService = Depends(get_picking_service),
):
    line = await service.pick_line(user_id=user_id, task_line_id=line_id, quantity=body.quantity)
    return {"id": line.id, "fact_qty": str(line.fact_qty), "plan_qty": str(line.plan_qty)}


@router.post(
    "/{task_id}/complete",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("complete", "tasks"))],
)
async def complete_picking(
    task_id: int,
    user_id: UserDep,
    service: PickingService = Depends(get_picking_service),
) -> TaskRead:
    task = await service.complete(user_id=user_id, task_id=task_id)
    return TaskRead.model_validate(task)
