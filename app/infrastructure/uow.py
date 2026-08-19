"""Unit of Work — управление транзакцией."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    """Управляет транзакцией: открывает сессию, коммитит или откатывает."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self._session = self._session_factory()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session is None:
            return

        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()

        await self._session.close()
        self._session = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork не открыт")
        return self._session
