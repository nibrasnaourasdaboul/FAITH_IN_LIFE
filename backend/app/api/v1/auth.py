from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import AppError
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    OtpRequest,
    RefreshRequest,
    RegisterRequest,
    ResendOtpRequest,
    ResetPasswordRequest,
)
from app.services import identity

router = APIRouter(prefix="/auth", tags=["auth"])


# يستخرج عنوان الجهاز الذي أرسل الطلب.
def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ينشئ حساباً جديداً ويرسل رمز التحقق إلى البريد.
@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)) -> MessageResponse:
    try:
        await identity.register_user(session, payload)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Check your email for the 6-digit verification code.", code="verification_sent")


# يطابق رمز التحقق ويفتح الجلسة بعد تأكيد البريد.
@router.post("/verify-email")
async def verify_email(payload: OtpRequest, request: Request, session: AsyncSession = Depends(get_db)):
    try:
        return await identity.verify_email(
            session,
            payload.email,
            payload.code,
            _client_ip(request),
            request.headers.get("user-agent"),
        )
    except AppError as exc:
        raise _http(exc) from exc


# يرسل رمز تحقق جديداً إلى البريد.
@router.post("/resend-otp", response_model=MessageResponse)
async def resend(payload: ResendOtpRequest, session: AsyncSession = Depends(get_db)) -> MessageResponse:
    purpose = payload.purpose if payload.purpose in {"verify", "reset"} else "verify"
    try:
        await identity.resend_otp(session, payload.email, purpose)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="If the account can receive a code, it has been sent.", code="otp_sent")


# يتحقق من البريد وكلمة المرور ثم يفتح الجلسة.
@router.post("/login")
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_db)):
    try:
        return await identity.login(
            session,
            payload.email,
            payload.password,
            payload.role,
            _client_ip(request),
            request.headers.get("user-agent"),
        )
    except AppError as exc:
        raise _http(exc) from exc


# يجدّد رمز الدخول باستخدام رمز التحديث.
@router.post("/refresh")
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_db)):
    try:
        return await identity.refresh_tokens(session, payload.refresh_token)
    except AppError as exc:
        raise _http(exc) from exc


# ينهي الجلسة الحالية ويلغي رمز التحديث.
@router.post("/logout", response_model=MessageResponse)
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_db)) -> MessageResponse:
    await identity.logout(session, payload.refresh_token)
    return MessageResponse(message="Signed out.", code="signed_out")


# يرسل رمز استعادة كلمة المرور إلى البريد.
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot(payload: ForgotPasswordRequest, session: AsyncSession = Depends(get_db)) -> MessageResponse:
    try:
        await identity.forgot_password(session, payload.email)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="If an account exists, a reset code is on its way.", code="reset_sent")


# يستبدل كلمة المرور بعد التحقق من الرمز.
@router.post("/reset-password", response_model=MessageResponse)
async def reset(payload: ResetPasswordRequest, session: AsyncSession = Depends(get_db)) -> MessageResponse:
    try:
        await identity.reset_password(session, payload.email, payload.code, payload.new_password)
    except AppError as exc:
        raise _http(exc) from exc
    return MessageResponse(message="Password updated. You can sign in.", code="password_reset")


# يحوّل خطأ المصادقة إلى استجابة HTTP.
def _http(exc: AppError):
    from fastapi import HTTPException

    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message})
