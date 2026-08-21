"""Удалить все заказы и связанные сущности."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import app.accounts.models  # noqa
import app.parties.models  # noqa
import app.warehouse.models  # noqa
import app.orders.models  # noqa
import app.documents.models  # noqa
import app.delivery.models  # noqa

from sqlalchemy import text
from app.core.database import async_session_factory


async def clear_orders():
    """Удалить заказы, документы, доставки."""
    async with async_session_factory() as session:
        # Доставка
        await session.execute(text('DELETE FROM delivery_deviation'))
        await session.execute(text('DELETE FROM delivery_route_line'))
        await session.execute(text('DELETE FROM delivery_route'))
        await session.execute(text('DELETE FROM delivery_order'))

        # Документы
        await session.execute(text('DELETE FROM documents_document_line'))
        await session.execute(text('DELETE FROM documents_document'))

        # Заказы
        await session.execute(text('DELETE FROM orders_return_line'))
        await session.execute(text('DELETE FROM orders_return'))
        await session.execute(text('DELETE FROM orders_outbound_line'))
        await session.execute(text('DELETE FROM orders_outbound'))
        await session.execute(text('DELETE FROM orders_inbound_line'))
        await session.execute(text('DELETE FROM orders_inbound'))

        await session.commit()
        print('✅ Заказы, документы, доставки удалены')


if __name__ == '__main__':
    asyncio.run(clear_orders())
