import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import AppError
from app.models import User
from app.schemas.auth import (
    GuardianLinkRequest,
    LinkDecision,
    LinkPublic,
    MessageResponse,
    NotificationPublic,
    PasswordChangeRequest,
    PreferencePatch,
    ProfilePatch,
    SessionPublic,
    UserPublic,
)
from app.services import accounts
from app.services.identity import build_profile, public_user

router = APIRouter(prefix="/users", tags=["users"])


# يحوّل خطأ الحساب إلى استجابة HTTP.
def _http(exc: AppError):
    from fastapi import HTTPException

    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message})


# يُرجع بيانات المستخدم الذي سجّل دخوله.
@router.get("/me", response_model=UserPublic)
async def me(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> dict:
    profile = await build_profile(session, user)
    return public_user(user, profile)


# يحدّث الاسم وبيانات الملف الشخصي.
@router.patch("/me", response_model=UserPublic)
async def patch_me(
    payload: ProfilePatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await accounts.update_profile(session, user, payload)
    except AppError as exc:
        raise _http(exc) from exc


# يغيّر كلمة المرور بعد التحقق من الحالية.
@router.post("/me/password", response_model=MessageResponse)
async def password(
    payload: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.change_password(session, user, payload.current_password, payload.new_password)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Password changed.", code="password_changed")


# يحفظ صورة الحساب الجديدة.
@router.post("/me/avatar", response_model=UserPublic)
async def avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    data = await file.read()
    try:
        return await accounts.save_avatar(session, user, file.filename or "avatar.png", data, file.content_type or "")
    except AppError as exc:
        raise _http(exc) from exc


# يحفظ تفضيلات التنبيه والخصوصية.
@router.patch("/me/preferences")
async def preferences(
    payload: PreferencePatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await accounts.update_preferences(session, user, payload)
    except AppError as exc:
        raise _http(exc) from exc


# يعرض الجلسات المفتوحة لهذا الحساب.
@router.get("/me/sessions", response_model=list[SessionPublic])
async def sessions(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    return await accounts.list_sessions(session, user)


# ينهي جلسة محددة من جهاز آخر.
@router.delete("/me/sessions/{session_id}", response_model=MessageResponse)
async def end_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.revoke_session(session, user, session_id)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Session ended.", code="session_ended")


# يعرض إشعارات المستخدم.
@router.get("/me/notifications", response_model=list[NotificationPublic])
async def notifications(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    return await accounts.list_notifications(session, user)


# يعلّم الإشعار كمقروء.
@router.post("/me/notifications/{notification_id}/read", response_model=MessageResponse)
async def read_notification(
    notification_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await accounts.mark_notification_read(session, user, notification_id)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Marked as read.", code="read")


# يعرض طلبات ربط الوصي بالمريض.
@router.get("/me/links", response_model=list[LinkPublic])
async def links(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    return await accounts.list_links(session, user)


# ينشئ طلب ربط بين الوصي والمريض.
@router.post("/me/links", status_code=201)
async def create_link(
    payload: GuardianLinkRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await accounts.guardian_request(session, user, payload.patient_email, payload.national_id)
    except AppError as exc:
        raise _http(exc) from exc


# يسجّل موافقة المريض أو رفضه لطلب الربط.
@router.post("/me/links/{link_id}/decision", response_model=LinkPublic)
async def decision(
    link_id: uuid.UUID,
    payload: LinkDecision,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        return await accounts.decide_link(session, user, link_id, payload.decision)
    except AppError as exc:
        raise _http(exc) from exc
