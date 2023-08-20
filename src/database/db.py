"""
Модуль для керування базою даних з використанням SQLAlchemy та асинхронних сесій.

Цей модуль містить класи та функції для підключення до бази даних, керування сесіями та
забезпечення доступу до бази даних у відповідності зі стандартами SQLAlchemy.

Classes:
    Base: Базовий клас для оголошення моделей SQLAlchemy.
    DatabaseSessionManager: Клас для керування сесіями бази даних SQLAlchemy.

Functions:
    get_db: Залежність для отримання асинхронної сесії бази даних.
"""
import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.conf.config import config


class Base(DeclarativeBase):
    """
    Базовий клас для оголошення моделей SQLAlchemy.
    """


class DatabaseSessionManager:
    """
    Клас для керування сесіями бази даних SQLAlchemy.
    """
    def __init__(self, url: str):
        """
        Ініціалізує об'єкт DatabaseSessionManager.

        :param url: URL бази даних для підключення.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker | None = async_sessionmaker(autocommit=False, autoflush=False,
                                                                            expire_on_commit=False,
                                                                            bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Контекстний менеджер для отримання асинхронної сесії бази даних.

        :return: Асинхронна сесія бази даних.
        """
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.sqlalchemy_database_url)


# Dependency
async def get_db():
    """
    Залежність для отримання асинхронної сесії бази даних.

    :return: Асинхронна сесія бази даних.
    """
    async with sessionmanager.session() as session:
        yield session
