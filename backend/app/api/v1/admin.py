import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.errors import AppError
from app.models import User
from app.schemas.auth import BanRequest, LicenseDecision, MessageResponse
from app.services import accounts

router = APIRouter(prefix="/admin", tags=["admin"])


# يحوّل خطأ التطبيق إلى استجابة HTTP للإدارة.
def _http(exc: AppError):
    from fastapi import HTTPException

    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message})


# يعرض قائمة الحسابات لمدير النظام.
@router.get("/users")
async def users(
    q: str | None = None,
    role: str | None = None,
    _: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
):
    return await accounts.admin_users(session, q, role)


# يوقف حساب مستخدم مع سبب الإيقاف.
@router.post("/users/{user_id}/ban", response_model=MessageResponse)
async def ban(
    user_id: uuid.UUID,
    payload: BanRequest,
    actor: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.ban_user(session, actor, user_id, payload.reason, payload.lifts_at)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Account suspended.", code="banned")


# يعيد تفعيل حساب كان موقوفاً.
@router.post("/users/{user_id}/unban", response_model=MessageResponse)
async def unban(
    user_id: uuid.UUID,
    _: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.unban_user(session, user_id)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Account restored.", code="unbanned")


# يعرض تراخيص الأطباء بانتظار المراجعة.
@router.get("/licenses")
async def licenses(_: User = Depends(require_roles("admin")), session: AsyncSession = Depends(get_db)):
    return await accounts.pending_licenses(session)


# يسجّل قرار المدير بقبول الترخيص أو رفضه.
@router.post("/licenses/{license_id}/review", response_model=MessageResponse)
async def review(
    license_id: uuid.UUID,
    payload: LicenseDecision,
    actor: User = Depends(require_roles("admin")),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.review_license(session, actor, license_id, payload.decision, payload.notes)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="License review saved.", code="license_reviewed")
