import os
from typing import Literal, Optional

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel


Role = Literal["developer", "risk_officer", "auditor", "admin"]


class UserContext(BaseModel):
    user_id: str
    role: Role


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Optional API key guard.

    If LIFEAI_API_KEY is configured, callers must provide a matching x-api-key.
    If not configured, authentication is effectively disabled for local development.
    """
    expected = os.getenv("LIFEAI_API_KEY")
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_user_context(
    x_user_id: Optional[str] = Header(default=None),
    x_user_role: Optional[str] = Header(default=None),
    _: None = Depends(verify_api_key),
) -> UserContext:
    """Lightweight user/role context placeholder for future RBAC workflow."""
    user_id = (x_user_id or "local-dev").strip()
    role = (x_user_role or "developer").strip().lower()

    allowed_roles = {"developer", "risk_officer", "auditor", "admin"}
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role}'. Allowed roles: {sorted(allowed_roles)}",
        )

    return UserContext(user_id=user_id, role=role)  # type: ignore[arg-type]
