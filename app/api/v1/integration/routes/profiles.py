"""API для профилей интеграции."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.integration.schemas import IntegrationProfileCreate, IntegrationProfileRead
from app.core.exceptions import NotFoundError
from app.integration.repository import IntegrationProfileRepository

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/profiles", response_model=list[IntegrationProfileRead], dependencies=[Depends(require_permission("view", "integrations"))])
async def list_profiles(services: Services) -> list[IntegrationProfileRead]:
    rows = await IntegrationProfileRepository(services.session).list_all()
    return [IntegrationProfileRead.model_validate(r) for r in rows]


@router.get("/profiles/{profile_id}", response_model=IntegrationProfileRead, dependencies=[Depends(require_permission("view", "integrations"))])
async def get_profile(profile_id: int, services: Services) -> IntegrationProfileRead:
    profile = await IntegrationProfileRepository(services.session).get_by_id(profile_id)
    if profile is None:
        raise NotFoundError("Профиль не найден")
    return IntegrationProfileRead.model_validate(profile)


@router.post("/profiles", response_model=IntegrationProfileRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "integrations"))])
async def create_profile(body: IntegrationProfileCreate, services: Services, user_id: UserDep) -> IntegrationProfileRead:
    profile = await IntegrationProfileRepository(services.session).create(**body.model_dump())
    return IntegrationProfileRead.model_validate(profile)


@router.patch("/profiles/{profile_id}", response_model=IntegrationProfileRead, dependencies=[Depends(require_permission("update", "integrations"))])
async def update_profile(profile_id: int, body: IntegrationProfileCreate, services: Services, user_id: UserDep) -> IntegrationProfileRead:
    profile = await IntegrationProfileRepository(services.session).update(profile_id, **body.model_dump(exclude_unset=True))
    if profile is None:
        raise NotFoundError("Профиль не найден")
    return IntegrationProfileRead.model_validate(profile)


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "integrations"))])
async def delete_profile(profile_id: int, services: Services, user_id: UserDep) -> None:
    ok = await IntegrationProfileRepository(services.session).soft_delete(profile_id, user_id)
    if not ok:
        raise NotFoundError("Профиль не найден")
