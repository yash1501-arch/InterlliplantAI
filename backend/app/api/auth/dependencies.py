from typing import Any

from fastapi import Depends, HTTPException, status

from app.api.auth.routes import get_current_user as _real_get_current_user
from app.config import settings


def _get_current_user_conditional() -> dict[str, Any]:
    if not settings.auth_enabled:
        return {"id": "test-user", "email": "test@intelliplant.ai", "name": "Test User", "role": "admin"}
    return _real_get_current_user()


def require_role(*roles: str):
    def checker(current_user: dict[str, Any] = Depends(_get_current_user_conditional)) -> dict[str, Any]:
        if not settings.auth_enabled:
            return current_user
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.get('role')} not authorized. Required: {', '.join(roles)}",
            )
        return current_user
    return checker
