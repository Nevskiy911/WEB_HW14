"""
Модуль, який надає функціональність для роботи з користувачами бази даних.

Цей модуль визначає функції для отримання, створення, оновлення та видалення користувачів
за допомогою SQLAlchemy.

.. moduleauthor:: Nevskiy911

"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Account
from src.schemas import UserSchema, UserUpdateSchema


async def get_users(limit: int, offset: int, db: AsyncSession, acc: Account):
    """
    Отримати список користувачів для певного облікового запису.

    :param limit: Максимальна кількість користувачів для повернення.
    :type limit: int
    :param offset: Кількість пропущених користувачів під час генерації.
    :type offset: int
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить список користувачів.
    :type acc: Account
    :return: Список користувачів.
    """
    sq = select(User).filter_by(acc=acc).offset(offset).limit(limit)
    users = await db.execute(sq)
    return users.scalars().all()


async def get_all_users(limit: int, offset: int, db: AsyncSession):
    """
    Отримати список всіх користувачів.

    :param limit: Максимальна кількість користувачів для повернення.
    :type limit: int
    :param offset: Кількість пропущених користувачів під час генерації.
    :type offset: int
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :return: Список всіх користувачів.
    """
    sq = select(User).offset(offset).limit(limit)
    users = await db.execute(sq)
    return users.scalars().all()


async def get_user(user_id: int, db: AsyncSession, acc: Account):
    """
    Отримати користувача за ідентифікатором для певного облікового запису.

    :param user_id: Ідентифікатор користувача, який буде повернений.
    :type user_id: int
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить ідентифікатор користувача.
    :type acc: Account
    :return: Користувач за ідентифікатором.
    """
    sq = select(User).filter_by(id=user_id, acc=acc)
    user = await db.execute(sq)
    return user.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession, acc: Account):
    """
    Створити користувача для певного облікового запису.

    :param body: Схема з даними для створення користувача.
    :type body: UserSchema
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить створений користувач.
    :type acc: Account
    :return: Створений користувач.
    """
    user = User(first_name=body.first_name, last_name=body.last_name, email=body.email, phone_number=body.phone_number,
                birthday=body.birthday, acc=acc)
    if body.data:
        user.data = body.data
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user_id: int, body: UserUpdateSchema, db: AsyncSession, acc: Account):
    """
    Оновити користувача для певного облікового запису.

    :param user_id: Ідентифікатор користувача, який буде оновлений.
    :type user_id: int
    :param body: Схема з даними для оновлення користувача.
    :type body: UserUpdateSchema
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить ідентифікатор користувача.
    :type acc: Account
    :return: Оновлений користувач.
    """
    sq = select(User).filter_by(id=user_id, acc=acc)
    result = await db.execute(sq)
    user = result.scalar_one_or_none()
    if user:
        user.first_name = body.first_name
        user.last_name = body.last_name
        user.email = body.email
        user.phone_number = body.phone_number
        user.birthday = body.birthday
        user.data = body.data
        await db.commit()
        await db.refresh(user)
    return user


async def remove_user(user_id: int, db: AsyncSession, acc: Account):
    """
    Видалити користувача для певного облікового запису.

    :param user_id: Ідентифікатор користувача, який буде видалений.
    :type user_id: int
    :param db: Сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить ідентифікатор користувача.
    :type acc: Account
    :return: Видалений користувач.
    """
    sq = select(User).filter_by(id=user_id, acc=acc)
    result = await db.execute(sq)
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
    return user
