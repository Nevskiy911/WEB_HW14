"""
Модуль, який надає функціональність для роботи з обліковими записами бази даних.

Цей модуль визначає функції для отримання, створення, оновлення облікових записів, а також
підтвердження email облікового запису.

.. moduleauthor:: Nevskiy911

"""
import logging

from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Account
from src.schemas import AccountSchema


async def get_acc_by_email(email: str, db: AsyncSession) -> Account:
    """
    Отримати обліковий запис за email.

    :param email: Email для пошуку облікового запису.
    :param db: Асинхронна сесія бази даних.
    :return: Об'єкт облікового запису або None, якщо обліковий запис не знайдено.
    """
    sq = select(Account).filter_by(email=email)
    result = await db.execute(sq)
    acc = result.scalar_one_or_none()
    logging.info(acc)
    return acc


async def create_acc(body: AccountSchema, db: AsyncSession) -> Account:
    """
    Створити новий обліковий запис.

    :param body: Об'єкт схеми з даними для створення облікового запису.
    :param db: Асинхронна сесія бази даних.
    :return: Об'єкт нового облікового запису.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        logging.error(e)
    new_acc = Account(**body.model_dump(), avatar=avatar)
    db.add(new_acc)
    await db.commit()
    await db.refresh(new_acc)
    return new_acc


async def update_token(user: Account, token: str | None, db: AsyncSession) -> None:
    """
    Оновити токен оновлення для облікового запису.

    :param user: Об'єкт облікового запису.
    :param token: Новий токен оновлення або None.
    :param db: Асинхронна сесія бази даних.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Підтвердити email облікового запису.

    :param email: Email для пошуку облікового запису.
    :param db: Асинхронна сесія бази даних.
    """
    user = await get_acc_by_email(email, db)
    user.confirmed = True
    await db.commit()