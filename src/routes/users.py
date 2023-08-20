"""
Модуль, який надає функціональність для роботи з користувачами за допомогою FastAPI.

Цей модуль визначає роутер, який містить функції для отримання списку користувачів, отримання деталей користувача,
створення, оновлення та видалення користувачів.

.. moduleauthor:: Nevskiy911

"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import Account, Role
from src.schemas import UserResponse, UserSchema, UserUpdateSchema
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/users', tags=["users"])
access_to_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[UserResponse])
async def get_users(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=200),
                    db: AsyncSession = Depends(get_db), acc: Account = Depends(auth_service.get_current_acc)):
    """
    Отримати список користувачів для певного облікового запису.

    :param limit: Максимальна кількість користувачів для повернення.
    :type limit: int
    :param offset: Кількість пропущених користувачів під час генерації.
    :type offset: int
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належать користувачі.
    :type acc: Account
    :return: Список користувачів.
    """
    users = await repository_users.get_users(limit, offset, db, acc)
    return users


@router.get("/all", response_model=List[UserResponse], dependencies=[Depends(access_to_all)])
async def get_users(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=200),
                    db: AsyncSession = Depends(get_db), acc: Account = Depends(auth_service.get_current_acc)):
    """
    Отримати список всіх користувачів (доступно адміністраторам та модераторам).

    :param limit: Максимальна кількість користувачів для повернення.
    :type limit: int
    :param offset: Кількість пропущених користувачів під час генерації.
    :type offset: int
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належать користувачі.
    :type acc: Account
    :return: Список користувачів.
    """
    users = await repository_users.get_all_users(limit, offset, db)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                   acc: Account = Depends(auth_service.get_current_acc)):
    """
    Отримати деталі користувача за ідентифікатором.

    :param user_id: Ідентифікатор користувача.
    :type user_id: int
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить користувач.
    :type acc: Account
    :return: Деталі користувача.
    """
    user = await repository_users.get_user(user_id, db, acc)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db),
                      acc: Account = Depends(auth_service.get_current_acc)):
    """
    Створити нового користувача.

    :param body: Дані для створення користувача.
    :type body: UserSchema
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить користувач.
    :type acc: Account
    :return: Створений користувач.
    """
    user = await repository_users.create_user(body, db, acc)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(body: UserUpdateSchema, user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      acc: Account = Depends(auth_service.get_current_acc)):
    """
    Оновити дані користувача.

    :param body: Нові дані для користувача.
    :type body: UserUpdateSchema
    :param user_id: Ідентифікатор користувача.
    :type user_id: int
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить користувач.
    :type acc: Account
    :return: Оновлені дані користувача.
    """
    user = await repository_users.update_user(user_id, body, db, acc)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      acc: Account = Depends(auth_service.get_current_acc)):
    """
    Видалити користувача за ідентифікатором.

    :param user_id: Ідентифікатор користувача.
    :type user_id: int
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :param acc: Обліковий запис, до якого належить користувач.
    :type acc: Account
    :return: Видалений користувач.
    """
    user = await repository_users.remove_user(user_id, db, acc)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
