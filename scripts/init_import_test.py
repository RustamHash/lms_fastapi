"""Инициализация данных для теста импорта."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import app.accounts.models  # noqa
import app.parties.models  # noqa
import app.warehouse.models  # noqa
import app.integration.models  # noqa
from app.core.database import async_session_factory
from app.parties.models import Depositor, LegalEntity
from app.warehouse.models import Warehouse, VirtualWarehouse, Zone, Row, Location
from app.integration.models import IntegrationProfile


async def init():
    async with async_session_factory() as session:
        # 1. Найти или создать юрлицо Зиландии
        legal_entity = await session.scalar(
            select(LegalEntity).where(LegalEntity.inn == "5044080919")
        )
        if not legal_entity:
            legal_entity = LegalEntity(
                name="ЗИЛАНДИЯ ООО",
                legal_name='ООО "ЗИЛАНДИЯ"',
                inn="5044080919",
                kpp="504701001",
            )
            session.add(legal_entity)
            await session.flush()
            print(f"Юрлицо создано: {legal_entity.id}")
        else:
            print(f"Юрлицо найдено: {legal_entity.id}")

        # 2. Найти или создать поклажедателя
        depositor = await session.scalar(
            select(Depositor).where(Depositor.code == "ZLN")
        )
        if not depositor:
            depositor = Depositor(
                legal_entity_id=legal_entity.id,
                code="ZLN",
            )
            session.add(depositor)
            await session.flush()
            print(f"Поклажедатель создан: {depositor.id}")
        else:
            print(f"Поклажедатель найден: {depositor.id}")

        # 3. Создать склад
        warehouse = Warehouse(name="Основной склад")
        session.add(warehouse)
        await session.flush()
        print(f"Склад создан: {warehouse.id}")

        # 4. Создать виртуальный склад
        vw = VirtualWarehouse(
            depositor_id=depositor.id,
            warehouse_id=warehouse.id,
            code="0000001",
            name="Зиландия основной",
        )
        session.add(vw)
        await session.flush()
        print(f"Виртуальный склад создан: {vw.id}")

        # 5. Создать зону хранения
        zone = Zone(
            warehouse_id=warehouse.id,
            name="Хранение",
            zone_type="storage",
        )
        session.add(zone)
        await session.flush()
        print(f"Зона создана: {zone.id}")

        # 6. Создать ряд
        row = Row(
            zone_id=zone.id,
            code="A",
            row_type="rack",
        )
        session.add(row)
        await session.flush()
        print(f"Ряд создан: {row.id}")

        # 7. Создать несколько ячеек
        for pos in range(1, 6):
            location = Location(
                row_id=row.id,
                position=pos,
                level=1,
            )
            session.add(location)
        await session.flush()
        print("Ячейки созданы: 5 шт")

        # 8. Создать профиль интеграции
        profile = IntegrationProfile(
            depositor_id=depositor.id,
            name="Зиландия FTP",
            source_type="ftp",
            config={
                "ftp": {
                    "host": "test.example.com",
                    "username": "test",
                    "password": "test",
                    "out_path": "/out",
                }
            },
        )
        session.add(profile)
        await session.flush()
        print(f"Профиль интеграции создан: {profile.id}")

        await session.commit()
        print("\nГотово!")


if __name__ == "__main__":
    from sqlalchemy import select
    asyncio.run(init())
