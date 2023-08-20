from typing import List

from fastapi import Request, Depends, HTTPException, status

from src.database.models import Role, Account
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, acc: Account = Depends(auth_service.get_current_acc)):
        if acc.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")