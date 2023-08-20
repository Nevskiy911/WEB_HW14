"""
Модуль, який надає функціональність для аутентифікації та авторизації користувачів за допомогою FastAPI.

Цей модуль визначає роутер, який містить функції для реєстрації, входу, оновлення токенів,
та підтвердження email користувачів.

.. moduleauthor:: Nevskiy911

"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import AccountSchema, AccountResponseSchema, TokenModel
from src.repository import acc as repository_accs
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=AccountResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: AccountSchema, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Зареєструвати нового користувача.

    :param body: Дані для створення облікового запису.
    :type body: AccountSchema
    :param background_tasks: Фонові завдання.
    :type background_tasks: BackgroundTasks
    :param request: Об'єкт запиту.
    :type request: Request
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :return: Створений обліковий запис.
    """
    exist_acc = await repository_accs.get_acc_by_email(body.email, db)
    if exist_acc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_acc = await repository_accs.create_acc(body, db)
    background_tasks.add_task(send_email, new_acc.email, new_acc.username, str(request.base_url))
    return new_acc


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Аутентифікація користувача та отримання токенів доступу.

    :param body: Форма запиту з даними аутентифікації.
    :type body: OAuth2PasswordRequestForm
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :return: Модель токенів доступу.
    """
    acc = await repository_accs.get_acc_by_email(body.username, db)
    if acc is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not acc.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, acc.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASS)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": acc.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": acc.email})
    await repository_accs.update_token(acc, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    """
    Оновлення токену доступу на основі токену оновлення.

    :param credentials: Креденшали доступу.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :return: Модель оновлених токенів доступу.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_accs.get_acc_by_email(email, db)
    if user.refresh_token != token:
        await repository_accs.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_accs.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/{username}')
async def refresh_token(username: str, db: AsyncSession = Depends(get_db)):
    """
    Перенаправлення на сторінку підтвердження email.

    :param username: Ім'я користувача.
    :type username: str
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :return: Об'єкт перенаправлення.
    """
    print("------------------------------")
    print(f"{username} відкрив наш email")
    print("------------------------------")
    return RedirectResponse("http://localhost:8000/static/check.png")


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Підтвердження email користувача.

    :param token: Токен підтвердження email.
    :type token: str
    :param db: Асинхронна сесія бази даних.
    :type db: AsyncSession
    :return: Підтвердження успішності.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_accs.get_acc_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERR)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_accs.confirmed_email(email, db)
    return {"message": "Email confirmed"}
