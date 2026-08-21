"""API для модуля parties."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.parties import schemas
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.parties.models import (
    Address,
    Depositor,
    LegalEntity,
    RawAddress,
    Tariff,
    TariffDocument,
)
from app.parties.repository import (
    AddressRepository,
    ClientRepository,
    ContractRepository,
    DepositorRepository,
    LegalEntityRepository,
    TariffRepository,
)
from app.parties.services import (
    AddressService,
    ClientService,
    ContractService,
    DepositorService,
    LegalEntityService,
    TariffService,
)

router = APIRouter(prefix="/parties", tags=["parties"])


# ========== Адреса ==========

@router.get("/addresses", response_model=list[schemas.AddressRead], dependencies=[Depends(require_permission("view", "addresses"))])
async def list_addresses(session: SessionDep) -> list[schemas.AddressRead]:
    service = AddressService(AddressRepository(session))
    rows = await service.list_all()
    return [schemas.AddressRead.model_validate(r) for r in rows]


@router.post("/addresses/resolve", response_model=schemas.AddressRead, dependencies=[Depends(require_permission("create", "addresses"))])
async def resolve_address(
    body: schemas.AddressResolve,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.AddressRead:
    service = AddressService(AddressRepository(session))
    address = await service.get_or_create(body.raw_text, body.source, user_id)
    return schemas.AddressRead.model_validate(address)


@router.get("/addresses/{address_id}", response_model=schemas.AddressRead, dependencies=[Depends(require_permission("view", "addresses"))])
async def get_address(address_id: int, session: SessionDep) -> schemas.AddressRead:
    service = AddressService(AddressRepository(session))
    row = await service.get_by_id(address_id)
    if row is None:
        raise NotFoundError("Адрес не найден")
    return schemas.AddressRead.model_validate(row)


@router.patch("/addresses/{address_id}", response_model=schemas.AddressRead, dependencies=[Depends(require_permission("update", "addresses"))])
async def update_address(
    address_id: int,
    body: schemas.AddressUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.AddressRead:
    service = AddressService(AddressRepository(session))
    address = await service.update(address_id, user_id, body.model_dump(exclude_unset=True))
    if address is None:
        raise NotFoundError("Адрес не найден")
    return schemas.AddressRead.model_validate(address)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "addresses"))])
async def delete_address(
    address_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    service = AddressService(AddressRepository(session))
    ok = await service.soft_delete(address_id, user_id)
    if not ok:
        raise NotFoundError("Адрес не найден")


# ========== Алиасы (сырые адреса) ==========

@router.get("/aliases", response_model=list[schemas.RawAddressRead], dependencies=[Depends(require_permission("view", "addresses"))])
async def list_aliases(
    session: SessionDep,
    limit: int = 1000,
    offset: int = 0,
) -> list[schemas.RawAddressRead]:
    stmt = (
        select(RawAddress)
        .where()
        .order_by(RawAddress.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = list(await session.scalars(stmt))
    result = []
    for r in rows:
        address = await session.get(Address, r.normalized_address_id)
        result.append(
            schemas.RawAddressRead(
                id=r.id,
                is_active=r.is_active,
                is_deleted=r.is_deleted,
                created_at=r.created_at,
                updated_at=r.updated_at,
                created_by_id=r.created_by_id,
                updated_by_id=r.updated_by_id,
                deleted_at=r.deleted_at,
                deleted_by_id=r.deleted_by_id,
                raw_text=r.raw_text,
                hash=r.hash,
                normalized_address_id=r.normalized_address_id,
                source=r.source,
                full_address=address.full_address if address else None,
            )
        )
    return result


@router.post(
    "/aliases",
    response_model=schemas.RawAddressRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "addresses"))],
)
async def create_alias(
    body: schemas.AliasCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.RawAddressRead:
    service = AddressService(AddressRepository(session))
    address = await service.get_or_create(body.raw_text, body.source, user_id)

    raw = await session.scalar(
        select(RawAddress).where(RawAddress.raw_text == body.raw_text)
    )

    return schemas.RawAddressRead(
        id=raw.id,
        is_active=raw.is_active,
        is_deleted=raw.is_deleted,
        created_at=raw.created_at,
        updated_at=raw.updated_at,
        created_by_id=raw.created_by_id,
        updated_by_id=raw.updated_by_id,
        deleted_at=raw.deleted_at,
        deleted_by_id=raw.deleted_by_id,
        raw_text=raw.raw_text,
        hash=raw.hash,
        normalized_address_id=raw.normalized_address_id,
        source=raw.source,
        full_address=address.full_address,
    )


@router.get("/aliases/{alias_id}", response_model=schemas.RawAddressRead, dependencies=[Depends(require_permission("view", "addresses"))])
async def get_alias(alias_id: int, session: SessionDep) -> schemas.RawAddressRead:
    raw = await session.get(RawAddress, alias_id)
    if raw is None or raw.is_deleted:
        raise NotFoundError("Вариант ввода не найден")
    return schemas.RawAddressRead(
        id=raw.id,
        is_active=raw.is_active,
        is_deleted=raw.is_deleted,
        created_at=raw.created_at,
        updated_at=raw.updated_at,
        created_by_id=raw.created_by_id,
        updated_by_id=raw.updated_by_id,
        deleted_at=raw.deleted_at,
        deleted_by_id=raw.deleted_by_id,
        raw_text=raw.raw_text,
        hash=raw.hash,
        normalized_address_id=raw.normalized_address_id,
        source=raw.source,
    )


@router.patch(
    "/aliases/{alias_id}",
    response_model=schemas.RawAddressRead,
    dependencies=[Depends(require_permission("update", "addresses"))],
)
async def update_alias(
    alias_id: int,
    body: schemas.AliasUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.RawAddressRead:
    raw = await session.get(RawAddress, alias_id)
    if raw is None or raw.is_deleted:
        raise NotFoundError("Вариант ввода не найден")

    if body.raw_text is not None:
        raw.raw_text = body.raw_text
        # Пересчитываем hash
        raw.hash = AddressService.get_hash(body.raw_text)
    if body.source is not None:
        raw.source = body.source
    if body.normalized_address_id is not None:
        raw.normalized_address_id = body.normalized_address_id

    raw.updated_by_id = user_id
    await session.flush()

    address = await session.get(Address, raw.normalized_address_id)
    return schemas.RawAddressRead(
        id=raw.id,
        raw_text=raw.raw_text,
        hash=raw.hash,
        normalized_address_id=raw.normalized_address_id,
        source=raw.source,
        full_address=address.full_address if address else None,
    )


@router.delete("/aliases/{alias_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "addresses"))])
async def delete_alias(alias_id: int, session: SessionDep, user_id: UserDep) -> None:
    raw = await session.get(RawAddress, alias_id)
    if raw is None or raw.is_deleted:
        raise NotFoundError("Вариант ввода не найден")
    raw.soft_delete(user_id)
    await session.flush()


# ========== Юрлица ==========

@router.get("/legal-entities", response_model=list[schemas.LegalEntityRead], dependencies=[Depends(require_permission("view", "legal_entities"))])
async def list_legal_entities(session: SessionDep) -> list[schemas.LegalEntityRead]:
    service = LegalEntityService(LegalEntityRepository(session))
    rows = await service.list_all()
    return [schemas.LegalEntityRead.model_validate(r) for r in rows]


@router.post("/legal-entities", response_model=schemas.LegalEntityRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "legal_entities"))])
async def create_legal_entity(
    body: schemas.LegalEntityCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.LegalEntityRead:
    service = LegalEntityService(LegalEntityRepository(session))
    try:
        row = await service.create(user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.LegalEntityRead.model_validate(row)


@router.patch("/legal-entities/{entity_id}", response_model=schemas.LegalEntityRead, dependencies=[Depends(require_permission("update", "legal_entities"))])
async def update_legal_entity(
    entity_id: int,
    body: schemas.LegalEntityUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.LegalEntityRead:
    service = LegalEntityService(LegalEntityRepository(session))
    row = await service.update(entity_id, user_id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Юрлицо не найдено")
    return schemas.LegalEntityRead.model_validate(row)


@router.delete("/legal-entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "legal_entities"))])
async def delete_legal_entity(entity_id: int, session: SessionDep, user_id: UserDep) -> None:
    service = LegalEntityService(LegalEntityRepository(session))
    ok = await service.soft_delete(entity_id, user_id)
    if not ok:
        raise NotFoundError("Юрлицо не найдено")


@router.get("/legal-entities/{entity_id}", response_model=schemas.LegalEntityRead, dependencies=[Depends(require_permission("view", "legal_entities"))])
async def get_legal_entity(entity_id: int, session: SessionDep) -> schemas.LegalEntityRead:
    service = LegalEntityService(LegalEntityRepository(session))
    row = await service.get_by_id(entity_id)
    if row is None:
        raise NotFoundError("Юрлицо не найдено")
    return schemas.LegalEntityRead.model_validate(row)


# ========== Поклажедатели ==========

@router.get("/depositors", response_model=list[schemas.DepositorRead], dependencies=[Depends(require_permission("view", "depositors"))])
async def list_depositors(session: SessionDep) -> list[schemas.DepositorRead]:
    service = DepositorService(DepositorRepository(session))
    rows = await service.list_all()
    result = []
    for r in rows:
        le = await session.get(LegalEntity, r.legal_entity_id)
        result.append(
            schemas.DepositorRead(
                id=r.id,
                legal_entity_id=r.legal_entity_id,
                code=r.code,
                legal_entity_name=le.name if le else "",
            )
        )
    return result


@router.post("/depositors", response_model=schemas.DepositorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "depositors"))])
async def create_depositor(
    body: schemas.DepositorCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DepositorRead:
    service = DepositorService(DepositorRepository(session))
    try:
        row = await service.create(body.legal_entity_id, body.code, user_id)
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.DepositorRead.model_validate(row)


@router.get("/depositors/{depositor_id}", response_model=schemas.DepositorRead, dependencies=[Depends(require_permission("view", "depositors"))])
async def get_depositor(depositor_id: int, session: SessionDep) -> schemas.DepositorRead:
    service = DepositorService(DepositorRepository(session))
    row = await service.get_by_id(depositor_id)
    if row is None:
        raise NotFoundError("Поклажедатель не найден")
    return schemas.DepositorRead.model_validate(row)


@router.patch("/depositors/{depositor_id}", response_model=schemas.DepositorRead, dependencies=[Depends(require_permission("update", "depositors"))])
async def update_depositor(
    depositor_id: int,
    body: schemas.DepositorUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DepositorRead:
    row = await session.get(Depositor, depositor_id)
    if row is None:
        raise NotFoundError("Поклажедатель не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by_id = user_id
    await session.flush()
    return schemas.DepositorRead.model_validate(row)


@router.delete("/depositors/{depositor_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "depositors"))])
async def delete_depositor(depositor_id: int, session: SessionDep, user_id: UserDep) -> None:
    row = await session.get(Depositor, depositor_id)
    if row is None:
        raise NotFoundError("Поклажедатель не найден")
    row.soft_delete(user_id)
    await session.flush()


# ========== Клиенты ==========

@router.get("/clients", response_model=list[schemas.ClientRead], dependencies=[Depends(require_permission("view", "clients"))])
async def list_clients(
    session: SessionDep,
    depositor_id: Annotated[int | None, Query(ge=1)] = None,
) -> list[schemas.ClientRead]:
    repo = ClientRepository(session)
    if depositor_id:
        rows = await repo.list_by_depositor(depositor_id)
    else:
        rows = await repo.list_all()
    return [schemas.ClientRead.model_validate(r) for r in rows]


@router.post("/clients", response_model=schemas.ClientRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "clients"))])
async def create_client(
    body: schemas.ClientCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ClientRead:
    service = ClientService(ClientRepository(session))
    try:
        row = await service.create(user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.ClientRead.model_validate(row)


@router.get("/clients/{client_id}", response_model=schemas.ClientRead, dependencies=[Depends(require_permission("view", "clients"))])
async def get_client(client_id: int, session: SessionDep) -> schemas.ClientRead:
    service = ClientService(ClientRepository(session))
    row = await service.get_by_id(client_id)
    if row is None:
        raise NotFoundError("Клиент не найден")
    return schemas.ClientRead.model_validate(row)


@router.patch("/clients/{client_id}", response_model=schemas.ClientRead, dependencies=[Depends(require_permission("update", "clients"))])
async def update_client(
    client_id: int,
    body: schemas.ClientUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ClientRead:
    service = ClientService(ClientRepository(session))
    row = await service.update(client_id, user_id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Клиент не найден")
    return schemas.ClientRead.model_validate(row)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "clients"))])
async def delete_client(client_id: int, session: SessionDep, user_id: UserDep) -> None:
    service = ClientService(ClientRepository(session))
    ok = await service.soft_delete(client_id, user_id)
    if not ok:
        raise NotFoundError("Клиент не найден")


# ========== Договоры ==========

@router.get("/contracts", response_model=list[schemas.ContractRead], dependencies=[Depends(require_permission("view", "contracts"))])
async def list_contracts(session: SessionDep) -> list[schemas.ContractRead]:
    repo = ContractRepository(session)
    rows = await repo.list_all()
    return [schemas.ContractRead.model_validate(r) for r in rows]


@router.post("/contracts", response_model=schemas.ContractRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "contracts"))])
async def create_contract(
    body: schemas.ContractCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ContractRead:
    service = ContractService(ContractRepository(session))
    try:
        row = await service.create(user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.ContractRead.model_validate(row)


@router.get("/contracts/{contract_id}", response_model=schemas.ContractRead, dependencies=[Depends(require_permission("view", "contracts"))])
async def get_contract(contract_id: int, session: SessionDep) -> schemas.ContractRead:
    service = ContractService(ContractRepository(session))
    row = await service.get_by_id(contract_id)
    if row is None:
        raise NotFoundError("Договор не найден")
    return schemas.ContractRead.model_validate(row)


@router.patch("/contracts/{contract_id}", response_model=schemas.ContractRead, dependencies=[Depends(require_permission("update", "contracts"))])
async def update_contract(
    contract_id: int,
    body: schemas.ContractUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ContractRead:
    service = ContractService(ContractRepository(session))
    row = await service.update(contract_id, user_id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Договор не найден")
    return schemas.ContractRead.model_validate(row)


@router.delete("/contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "contracts"))])
async def delete_contract(contract_id: int, session: SessionDep, user_id: UserDep) -> None:
    service = ContractService(ContractRepository(session))
    ok = await service.soft_delete(contract_id, user_id)
    if not ok:
        raise NotFoundError("Договор не найден")


# ========== Тарифы ==========

@router.get("/tariff-documents", response_model=list[schemas.TariffDocumentRead], dependencies=[Depends(require_permission("view", "tariffs"))])
async def list_tariff_documents(session: SessionDep) -> list[schemas.TariffDocumentRead]:
    rows = list(await session.scalars(select(TariffDocument).where()))
    return [schemas.TariffDocumentRead.model_validate(r) for r in rows]


@router.get("/tariff-documents/{doc_id}", response_model=schemas.TariffDocumentRead, dependencies=[Depends(require_permission("view", "tariffs"))])
async def get_tariff_document(doc_id: int, session: SessionDep) -> schemas.TariffDocumentRead:
    service = TariffService(TariffRepository(session))
    doc = await service.get_document(doc_id)
    if doc is None:
        raise NotFoundError("Тарифный документ не найден")
    return schemas.TariffDocumentRead.model_validate(doc)


@router.patch("/tariff-documents/{doc_id}", response_model=schemas.TariffDocumentRead, dependencies=[Depends(require_permission("update", "tariffs"))])
async def update_tariff_document(
    doc_id: int,
    body: schemas.TariffDocumentUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TariffDocumentRead:
    doc = await session.get(TariffDocument, doc_id)
    if doc is None:
        raise NotFoundError("Тарифный документ не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    doc.updated_by_id = user_id
    await session.flush()
    return schemas.TariffDocumentRead.model_validate(doc)


@router.delete("/tariff-documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tariffs"))])
async def delete_tariff_document(doc_id: int, session: SessionDep, user_id: UserDep) -> None:
    doc = await session.get(TariffDocument, doc_id)
    if doc is None:
        raise NotFoundError("Тарифный документ не найден")
    doc.soft_delete(user_id)
    await session.flush()


@router.post("/tariff-documents", response_model=schemas.TariffDocumentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tariffs"))])
async def create_tariff_document(
    body: schemas.TariffDocumentCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TariffDocumentRead:
    service = TariffService(TariffRepository(session))
    try:
        row = await service.create_document(user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.TariffDocumentRead.model_validate(row)


@router.get("/tariffs", response_model=list[schemas.TariffRead], dependencies=[Depends(require_permission("view", "tariffs"))])
async def list_tariffs(session: SessionDep, document_id: int | None = None) -> list[schemas.TariffRead]:
    stmt = select(Tariff).where()
    if document_id:
        stmt = stmt.where(Tariff.document_id == document_id)
    rows = list(await session.scalars(stmt))
    return [schemas.TariffRead.model_validate(r) for r in rows]


@router.get("/tariffs/{tariff_id}", response_model=schemas.TariffRead, dependencies=[Depends(require_permission("view", "tariffs"))])
async def get_tariff(tariff_id: int, session: SessionDep) -> schemas.TariffRead:
    tariff = await session.get(Tariff, tariff_id)
    if tariff is None:
        raise NotFoundError("Тариф не найден")
    return schemas.TariffRead.model_validate(tariff)


@router.patch("/tariffs/{tariff_id}", response_model=schemas.TariffRead, dependencies=[Depends(require_permission("update", "tariffs"))])
async def update_tariff(
    tariff_id: int,
    body: schemas.TariffUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TariffRead:
    tariff = await session.get(Tariff, tariff_id)
    if tariff is None:
        raise NotFoundError("Тариф не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tariff, field, value)
    tariff.updated_by_id = user_id
    await session.flush()
    return schemas.TariffRead.model_validate(tariff)


@router.delete("/tariffs/{tariff_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tariffs"))])
async def delete_tariff(tariff_id: int, session: SessionDep, user_id: UserDep) -> None:
    tariff = await session.get(Tariff, tariff_id)
    if tariff is None:
        raise NotFoundError("Тариф не найден")
    tariff.soft_delete(user_id)
    await session.flush()


@router.post("/tariffs", response_model=schemas.TariffRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tariffs"))])
async def create_tariff(
    body: schemas.TariffCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TariffRead:
    service = TariffService(TariffRepository(session))
    try:
        row = await service.create_tariff(user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.TariffRead.model_validate(row)
