"""
Модуль, який визначає моделі користувачів та облікових записів з використанням SQLAlchemy.

Цей модуль містить класи, які відображають сутності "Користувач" та "Обліковий запис"
для збереження у базі даних, а також перерахування "Роль" для облікового запису.

Classes:
    User: Модель користувача для зберігання інформації про користувачів.
    Role: Перерахування, що визначає можливі ролі облікового запису користувача.
    Account: Модель облікового запису для зберігання інформації про облікові записи користувачів.
"""

import enum
from datetime import date

from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.db import Base


class User(Base):
    """
    Модель користувача для зберігання інформації про користувачів.

    :cvar __tablename__: Назва таблиці в базі даних.
    :cvar id: Унікальний ідентифікатор користувача.
    :cvar first_name: Ім'я користувача.
    :cvar last_name: Прізвище користувача.
    :cvar email: Email користувача.
    :cvar phone_number: Номер телефону користувача.
    :cvar birthday: День народження користувача.
    :cvar data: Додаткові дані користувача.
    :cvar created_at: Дата створення запису про користувача.
    :cvar updated_at: Дата оновлення запису про користувача.
    :cvar acc_id: Ідентифікатор облікового запису користувача.
    :cvar acc: Зв'язок з моделлю облікового запису.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150), index=True)
    email: Mapped[str] = mapped_column(String(150))
    phone_number: Mapped[str] = mapped_column(String(30))
    birthday: Mapped[str] = mapped_column(String(30))
    data: Mapped[bool] = mapped_column(default=False, nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)
    acc_id: Mapped[int] = mapped_column(Integer, ForeignKey("acc.id"), nullable=True)
    acc: Mapped["Account"] = relationship('Account', backref="users", lazy='joined')


class Role(enum.Enum):
    """
    Перерахування, що визначає можливі ролі облікового запису користувача.

    :cvar admin: Роль адміністратора.
    :cvar moderator: Роль модератора.
    :cvar user: Роль звичайного користувача.
    """
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class Account(Base):
    """
    Модель облікового запису для зберігання інформації про облікові записи користувачів.

    :cvar __tablename__: Назва таблиці в базі даних.
    :cvar id: Унікальний ідентифікатор облікового запису.
    :cvar username: Ім'я користувача облікового запису.
    :cvar email: Email облікового запису.
    :cvar password: Хеш паролю облікового запису.
    :cvar created_at: Дата створення облікового запису.
    :cvar updated_at: Дата оновлення облікового запису.
    :cvar avatar: Шлях до аватара користувача.
    :cvar refresh_token: Токен оновлення для аутентифікації.
    :cvar role: Роль облікового запису.
    :cvar confirmed: Підтвердження облікового запису.
    """
    __tablename__ = "acc"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
