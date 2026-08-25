"""Воркфлоу приёмки."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import get_receiving_service
from app.api.v1.warehouse.schemas.tasks import TaskRead
from app.api.v1.warehouse.schemas.workflow import (
    ReceiveLineBody,
    ReceivingCompleteBody,
    ReceivingFromInbound,
)
from app.warehouse.services.receiving_service import ReceivingService

router = APIRouter(prefix="/warehouse/receiving", tags=["warehouse-receiving"])


@router.post(
    "/from-inbound",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("create", "tasks"))],
)
async def create_receiving_from_inbound(
    body: ReceivingFromInbound,
    user_id: UserDep,
    service: ReceivingService = Depends(get_receiving_service),
) -> TaskRead:
    task = await service.create_from_inbound(
        user_id=user_id,
        inbound_order_id=body.inbound_order_id,
        receiving_location_id=body.receiving_location_id,
    )
    return TaskRead.model_validate(task)


@router.post(
    "/lines/{line_id}/receive",
    dependencies=[Depends(require_permission("execute", "tasks"))],
)
async def receive_line(
    line_id: int,
    body: ReceiveLineBody,
    user_id: UserDep,
    service: ReceivingService = Depends(get_receiving_service),
):
    line = await service.receive_line(
        user_id=user_id,
        task_line_id=line_id,
        quantity=body.quantity,
        batch_number=body.batch_number,
        location_id=body.location_id,
        lpn_id=body.lpn_id,
        manufacture_date=body.manufacture_date,
    )
    return {"id": line.id, "fact_qty": str(line.fact_qty), "plan_qty": str(line.plan_qty)}


@router.post(
    "/{task_id}/complete",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("complete", "tasks"))],
)
async def complete_receiving(
    task_id: int,
    body: ReceivingCompleteBody,
    user_id: UserDep,
    service: ReceivingService = Depends(get_receiving_service),
) -> TaskRead:
    task = await service.complete(
        user_id=user_id, task_id=task_id, confirm_shortage=body.confirm_shortage
    )
    return TaskRead.model_validate(task)


@router.post(
    "/movements/{movement_id}/cancel",
    status_code=204,
    dependencies=[Depends(require_permission("cancel", "tasks"))],
)
async def cancel_receiving_movement(
    movement_id: int,
    user_id: UserDep,
    service: ReceivingService = Depends(get_receiving_service),
) -> None:
    await service.cancel_movement(user_id=user_id, movement_id=movement_id)
