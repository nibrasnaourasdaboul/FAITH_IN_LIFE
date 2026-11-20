import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models import User
from app.services.identity import role_codes

bearer = HTTPBearer(auto_error=False)


# يقرأ رمز الدخول ويُرجع المستخدم الحالي بعد التحقق من حالة الحساب.
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Access token is not valid.") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Access token is not valid.")
    user = await session.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="Account was not found.")
    if user.account_status == "banned":
        raise HTTPException(status_code=403, detail="This account is suspended.")
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email verification is required.")
    return user


# يبني حاجزاً يسمح بالوصول فقط للأدوار المحددة.
def require_roles(*allowed: str) -> Callable:
    # يقارن أدوار المستخدم بالأدوار المسموح لها في هذا المسار.
    async def checker(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> User:
        codes = await role_codes(session, user.user_id)
        if not any(role in codes for role in allowed):
            raise HTTPException(status_code=403, detail="You do not have access to this area.")
        return user

    return checker
