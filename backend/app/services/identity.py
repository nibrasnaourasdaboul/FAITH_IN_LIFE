import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    new_otp,
    otp_matches,
    verify_password,
)
from app.models import (
    AdminProfile,
    AuthToken,
    CareEpisode,
    ClinicalComplaint,
    CommunityShareConsent,
    ConsentPolicy,
    DemographicProfile,
    DoctorProfile,
    GamificationProfile,
    GuardianProfile,
    LicenseCredential,
    LoginAttempt,
    LoginSession,
    MedicalHistoryEntry,
    MedicalRecord,
    NotificationPreference,
    PasswordResetRequest,
    PatientGuardianLink,
    PatientProfile,
    PrivacyConsent,
    Role,
    SpecialtyExpertise,
    User,
    UserRole,
)
from app.services.email_service import send_otp
from app.services.notifications import notify_user

ROLE_HOME = {
    "patient": "/app/patient",
    "doctor": "/app/doctor",
    "guardian": "/app/guardian",
    "admin": "/app/admin",
}


# يُرجع الوقت الحالي بالتوقيت العالمي.
def _now() -> datetime:
    return datetime.now(timezone.utc)


# يجلب رموز أدوار المستخدم من قاعدة البيانات.
async def role_codes(session: AsyncSession, user_id: uuid.UUID) -> list[str]:
    result = await session.execute(
        select(Role.role_code)
        .join(UserRole, UserRole.role_id == Role.role_id)
        .where(UserRole.user_id == user_id)
    )
    return [code for code in result.scalars().all() if code]


# يجمع بيانات الملف حسب دور المريض أو الطبيب أو الوصي أو المدير.
async def build_profile(session: AsyncSession, user: User) -> dict:
    roles = await role_codes(session, user.user_id)
    profile: dict = {"roles": roles}
    if "patient" in roles:
        patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
        if patient:
            profile["patient_id"] = patient.patient_id
            profile["birth_date"] = patient.birth_date.isoformat() if patient.birth_date else None
            profile["gender"] = patient.gender
            profile["national_id"] = patient.national_id
            profile["occupation"] = patient.occupation
            profile["work_posture_notes"] = patient.work_posture_notes
            profile["primary_language"] = patient.primary_language
    if "doctor" in roles:
        doctor = await session.scalar(select(DoctorProfile).where(DoctorProfile.user_id == user.user_id))
        if doctor:
            license_row = await session.scalar(
                select(LicenseCredential)
                .where(LicenseCredential.doctor_id == doctor.doctor_id)
                .order_by(LicenseCredential.issue_date.desc().nulls_last())
            )
            expertise = await session.scalar(
                select(SpecialtyExpertise).where(SpecialtyExpertise.doctor_id == doctor.doctor_id)
            )
            profile.update(
                {
                    "doctor_id": doctor.doctor_id,
                    "medical_title": doctor.medical_title,
                    "clinic_name": doctor.clinic_name,
                    "is_verified": bool(doctor.is_verified),
                    "license_number": license_row.license_number if license_row else None,
                    "license_status": license_row.status if license_row else None,
                    "specialization": doctor.specialization or (expertise.specialty_name if expertise else None),
                    "years_of_experience": doctor.years_of_experience,
                    "is_available": bool(doctor.is_available),
                }
            )
    if "guardian" in roles:
        guardian = await session.scalar(select(GuardianProfile).where(GuardianProfile.user_id == user.user_id))
        if guardian:
            profile.update(
                {
                    "guardian_id": guardian.guardian_id,
                    "relationship_type": guardian.relationship_type,
                    "emergency_contact": bool(guardian.emergency_contact),
                }
            )
    if "admin" in roles:
        admin = await session.scalar(select(AdminProfile).where(AdminProfile.user_id == user.user_id))
        if admin:
            profile.update({"admin_id": admin.admin_id})
    prefs = await session.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user.user_id))
    if prefs:
        profile["preferences"] = {
            "medical_alerts_enabled": bool(prefs.medical_alerts_enabled),
            "session_reminders_enabled": bool(prefs.session_reminders_enabled),
            "emergency_alerts_enabled": bool(prefs.emergency_alerts_enabled),
            "channel_preference": prefs.channel_preference,
        }
    if "patient" in roles and profile.get("patient_id"):
        record = await session.scalar(
            select(MedicalRecord)
            .join(CareEpisode, CareEpisode.episode_id == MedicalRecord.episode_id)
            .where(CareEpisode.patient_id == profile["patient_id"])
        )
        consent = None
        if record:
            consent = await session.scalar(
                select(CommunityShareConsent)
                .where(CommunityShareConsent.record_id == record.record_id)
                .order_by(CommunityShareConsent.approved_at.desc().nulls_last())
            )
        profile["community_share_enabled"] = bool(consent and consent.status == "approved" and consent.revoked_at is None)
        profile["record_id"] = record.record_id if record else None
    return profile


# يجهّز بيانات المستخدم الآمنة للواجهة دون كلمة المرور.
def public_user(user: User, profile: dict) -> dict:
    return {
        "user_id": user.user_id,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "account_status": user.account_status,
        "email_verified": user.email_verified,
        "preferred_locale": user.preferred_locale,
        "avatar_uri": user.avatar_uri,
        "roles": profile.get("roles", []),
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "profile": profile,
    }


# يجلب دور النظام المطلوب أو يوقف العملية إذا لم يُزرع.
async def _role(session: AsyncSession, code: str) -> Role:
    role = await session.scalar(select(Role).where(Role.role_code == code))
    if role is None:
        raise AppError("roles_not_seeded", 500, "Roles are not initialized.")
    return role


# يجلب سياسة الخصوصية المعتمدة.
async def _policy(session: AsyncSession) -> ConsentPolicy | None:
    return await session.scalar(select(ConsentPolicy).where(ConsentPolicy.policy_code == "privacy"))


# ينشئ رمز تحقق ويحفظ بصمته ثم يرسله بالبريد.
async def issue_otp(session: AsyncSession, user: User, purpose: str) -> None:
    code = new_otp()
    expires = _now() + timedelta(minutes=get_settings().otp_minutes)
    digest = hash_token(code)
    if purpose == "reset":
        session.add(
            PasswordResetRequest(
                user_id=user.user_id,
                token_hash=digest,
                expires_at=expires,
                used=False,
            )
        )
    else:
        session.add(
            AuthToken(
                user_id=user.user_id,
                token_type="email_otp",
                token_hash=digest,
                expires_at=expires,
                revoked=False,
            )
        )
    redis = await get_redis()
    if redis is not None:
        await redis.set(f"otp:{purpose}:{user.user_id}", digest, ex=get_settings().otp_minutes * 60)
    await send_otp(user.email or "", user.preferred_locale or "ar", "verify" if purpose == "verify" else "reset", code)


# ينشئ المستخدم ودوره وملفه ثم يرسل رمز تأكيد البريد.
async def register_user(session: AsyncSession, data) -> dict:
    email = data.email.lower()
    existing = await session.scalar(select(User).where(func.lower(User.email) == email))
    if existing:
        raise AppError("email_taken", 409, "An account with this email already exists.")

    now = _now()
    user = User(
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        full_name=data.full_name.strip(),
        account_status="pending_verification",
        mfa_enabled=False,
        created_at=now,
        email_verified=False,
        preferred_locale=data.locale,
    )
    session.add(user)
    await session.flush()

    role = await _role(session, data.role)
    session.add(UserRole(user_id=user.user_id, role_id=role.role_id, assigned_at=now))
    session.add(
        NotificationPreference(
            user_id=user.user_id,
            medical_alerts_enabled=True,
            session_reminders_enabled=True,
            emergency_alerts_enabled=True,
            channel_preference="email",
        )
    )
    policy = await _policy(session)
    if policy:
        session.add(
            PrivacyConsent(
                user_id=user.user_id,
                policy_id=policy.policy_id,
                consent_scope="account",
                accepted=True,
                accepted_at=now,
            )
        )

    if data.role == "patient" and data.patient:
        await _create_patient(session, user, data.patient, now)
    elif data.role == "doctor" and data.doctor:
        await _create_doctor(session, user, data.doctor)
    elif data.role == "guardian" and data.guardian:
        guardian = GuardianProfile(
            user_id=user.user_id,
            relationship_type=data.guardian.relationship_type,
            emergency_contact=data.guardian.emergency_contact,
        )
        session.add(guardian)
        await session.flush()
        if data.guardian.patient_email:
            try:
                await request_guardian_link(
                    session,
                    guardian,
                    user,
                    patient_email=str(data.guardian.patient_email),
                    national_id=None,
                )
            except AppError as exc:
                if exc.code != "patient_not_found":
                    raise

    await issue_otp(session, user, "verify")
    await session.commit()
    return {"email": user.email, "message": "verification_sent"}


# ينشئ ملف المريض وحلقة الرعاية والسجل الطبي الأولي.
async def _create_patient(session: AsyncSession, user: User, data, now: datetime) -> PatientProfile:
    patient = PatientProfile(
        user_id=user.user_id,
        birth_date=data.birth_date,
        gender=data.gender,
        national_id=data.national_id,
        occupation=data.occupation,
        work_posture_notes=data.work_posture_notes,
        primary_language=user.preferred_locale,
    )
    session.add(patient)
    await session.flush()
    episode = CareEpisode(
        patient_id=patient.patient_id,
        episode_title=data.health_condition[:180],
        injury_type=data.health_condition[:180],
        status="intake",
        opened_on=now.date(),
    )
    session.add(episode)
    await session.flush()
    record = MedicalRecord(
        episode_id=episode.episode_id,
        record_status="open",
        opened_at=now,
        last_updated_at=now,
        encryption_status="at_rest",
    )
    session.add(record)
    await session.flush()
    session.add(DemographicProfile(record_id=record.record_id))
    if data.medical_history:
        session.add(
            MedicalHistoryEntry(
                record_id=record.record_id,
                history_type="patient_reported",
                description=data.medical_history,
                event_date=now.date(),
                source="registration",
            )
        )
    session.add(
        ClinicalComplaint(
            patient_id=patient.patient_id,
            episode_id=episode.episode_id,
            chief_complaint=data.health_condition,
            pain_level=str(data.pain_level),
            onset_notes=data.work_posture_notes,
            submitted_at=now,
            status="submitted",
        )
    )
    session.add(
        GamificationProfile(
            patient_id=patient.patient_id,
            total_points=0,
            current_level="start",
            streak_days=0,
        )
    )
    return patient


# ينشئ ملف الطبيب وطلب الترخيص بانتظار المراجعة.
async def _create_doctor(session: AsyncSession, user: User, data) -> None:
    taken = await session.scalar(
        select(LicenseCredential).where(LicenseCredential.license_number == data.license_number)
    )
    if taken:
        raise AppError("license_taken", 409, "This license number is already registered.")
    doctor = DoctorProfile(
        user_id=user.user_id,
        professional_type="clinician",
        medical_title=data.medical_title,
        specialization=data.specialization,
        years_of_experience=data.years_of_experience,
        clinic_name=data.clinic_name,
        is_verified=False,
        is_available=False,
    )
    session.add(doctor)
    await session.flush()
    session.add(
        LicenseCredential(
            doctor_id=doctor.doctor_id,
            license_number=data.license_number,
            issuing_authority=data.issuing_authority,
            issue_date=data.issue_date,
            expiry_date=data.expiry_date,
            status="pending",
        )
    )
    session.add(
        SpecialtyExpertise(
            doctor_id=doctor.doctor_id,
            specialty_name=data.specialization,
            expertise_level=str(data.years_of_experience),
        )
    )


# يلغي الرمز السابق ويرسل رمزاً جديداً.
async def resend_otp(session: AsyncSession, email: str, purpose: str) -> None:
    user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user and purpose == "verify" and not user.email_verified:
        await session.execute(
            update(AuthToken)
            .where(AuthToken.user_id == user.user_id, AuthToken.token_type == "email_otp", AuthToken.revoked.is_(False))
            .values(revoked=True)
        )
        await issue_otp(session, user, "verify")
        await session.commit()
    elif user and purpose == "reset":
        await issue_otp(session, user, "reset")
        await session.commit()


# يؤكد البريد إذا طابق الرمز ثم يفتح الجلسة.
async def verify_email(session: AsyncSession, email: str, code: str, ip: str | None, device: str | None) -> dict:
    user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user is None:
        raise AppError("invalid_code", 400, "The verification code is not valid.")
    token = await session.scalar(
        select(AuthToken)
        .where(
            AuthToken.user_id == user.user_id,
            AuthToken.token_type == "email_otp",
            AuthToken.revoked.is_(False),
        )
        .order_by(AuthToken.expires_at.desc())
    )
    if token is None or token.expires_at is None or token.expires_at < _now() or not token.token_hash:
        raise AppError("invalid_code", 400, "The verification code is not valid.")
    if not otp_matches(code, token.token_hash):
        raise AppError("invalid_code", 400, "The verification code is not valid.")
    token.revoked = True
    user.email_verified = True
    user.account_status = "active"
    await session.flush()
    pair = await _open_session(session, user, ip, device)
    await session.commit()
    return pair


# يعد محاولات الدخول الفاشلة الأخيرة.
async def _recent_failures(session: AsyncSession, user_id: uuid.UUID) -> int:
    since = _now() - timedelta(minutes=15)
    result = await session.scalar(
        select(func.count())
        .select_from(LoginAttempt)
        .where(
            LoginAttempt.user_id == user_id,
            LoginAttempt.success.is_(False),
            LoginAttempt.attempted_at >= since,
        )
    )
    return int(result or 0)


# يتحقق من الحساب وكلمة المرور ويفتح الجلسة المناسبة.
async def login(session: AsyncSession, email: str, password: str, role: str | None, ip: str | None, device: str | None) -> dict:
    user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user and await _recent_failures(session, user.user_id) >= 5:
        raise AppError("locked", 429, "Too many attempts. Try again in a few minutes.")

    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        if user:
            session.add(
                LoginAttempt(
                    user_id=user.user_id,
                    success=False,
                    ip_address=ip,
                    failure_reason="invalid_credentials",
                    attempted_at=_now(),
                )
            )
            await session.commit()
        raise AppError("invalid_credentials", 401, "Email or password is incorrect.")

    if user.account_status == "banned":
        raise AppError("banned", 403, "This account is suspended.")
    if not user.email_verified or user.account_status == "pending_verification":
        raise AppError("email_not_verified", 403, "Verify your email before signing in.")

    roles = await role_codes(session, user.user_id)
    if role and role not in roles:
        raise AppError("wrong_role", 403, "This account does not have the selected role.")

    session.add(
        LoginAttempt(
            user_id=user.user_id,
            success=True,
            ip_address=ip,
            failure_reason=None,
            attempted_at=_now(),
        )
    )
    user.last_login_at = _now()
    pair = await _open_session(session, user, ip, device)
    await session.commit()
    return pair


# ينشئ جلسة دخول ويصدر رمزي الدخول والتحديث.
async def _open_session(session: AsyncSession, user: User, ip: str | None, device: str | None) -> dict:
    login_session = LoginSession(
        user_id=user.user_id,
        device_info=json.dumps({"user_agent": device or "unknown"}),
        ip_address=ip,
        status="active",
        started_at=_now(),
    )
    session.add(login_session)
    await session.flush()
    refresh, jti, expires = create_refresh_token(user.user_id, login_session.session_id)
    digest = hash_token(jti)
    info = {"user_agent": device or "unknown", "refresh_hash": digest}
    login_session.device_info = json.dumps(info)
    session.add(
        AuthToken(
            user_id=user.user_id,
            token_type="refresh",
            token_hash=digest,
            expires_at=expires,
            revoked=False,
        )
    )
    roles = await role_codes(session, user.user_id)
    access = create_access_token(user.user_id, roles)
    profile = await build_profile(session, user)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": get_settings().access_token_minutes * 60,
        "user": public_user(user, profile),
        "home": ROLE_HOME.get(roles[0], "/app") if roles else "/app",
    }


# يستبدل رمز التحديث القديم بزوج رموز جديد.
async def refresh_tokens(session: AsyncSession, raw_token: str) -> dict:
    try:
        payload = decode_token(raw_token)
    except ValueError as exc:
        raise AppError("invalid_token", 401, "Refresh token is not valid.") from exc
    if payload.get("type") != "refresh":
        raise AppError("invalid_token", 401, "Refresh token is not valid.")
    user = await session.get(User, uuid.UUID(payload["sub"]))
    if user is None or user.account_status in {"banned", "pending_verification"}:
        raise AppError("invalid_token", 401, "Refresh token is not valid.")
    digest = hash_token(payload["jti"])
    stored = await session.scalar(
        select(AuthToken).where(
            AuthToken.user_id == user.user_id,
            AuthToken.token_hash == digest,
            AuthToken.token_type == "refresh",
            AuthToken.revoked.is_(False),
        )
    )
    if stored is None or stored.expires_at is None or stored.expires_at < _now():
        raise AppError("invalid_token", 401, "Refresh token is not valid.")
    stored.revoked = True
    session_id = uuid.UUID(payload["sid"])
    login_session = await session.get(LoginSession, session_id)
    if login_session is None or login_session.status != "active":
        raise AppError("invalid_token", 401, "Session has ended.")
    refresh, jti, expires = create_refresh_token(user.user_id, session_id)
    new_digest = hash_token(jti)
    info = json.loads(login_session.device_info or "{}")
    info["refresh_hash"] = new_digest
    login_session.device_info = json.dumps(info)
    session.add(
        AuthToken(
            user_id=user.user_id,
            token_type="refresh",
            token_hash=new_digest,
            expires_at=expires,
            revoked=False,
        )
    )
    roles = await role_codes(session, user.user_id)
    await session.commit()
    return {
        "access_token": create_access_token(user.user_id, roles),
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": get_settings().access_token_minutes * 60,
    }


# ينهي الجلسة ويلغي رمز التحديث.
async def logout(session: AsyncSession, raw_token: str | None) -> None:
    if not raw_token:
        return
    try:
        payload = decode_token(raw_token)
    except ValueError:
        return
    digest = hash_token(payload.get("jti", ""))
    await session.execute(
        update(AuthToken).where(AuthToken.token_hash == digest).values(revoked=True)
    )
    if payload.get("sid"):
        login_session = await session.get(LoginSession, uuid.UUID(payload["sid"]))
        if login_session:
            login_session.status = "ended"
            login_session.ended_at = _now()
    await session.commit()


# يرسل رمز استعادة إذا كان الحساب موجوداً وغير موقوف.
async def forgot_password(session: AsyncSession, email: str) -> None:
    user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user and user.account_status != "banned":
        await issue_otp(session, user, "reset")
        await session.commit()


# يغيّر كلمة المرور بعد مطابقة رمز الاستعادة.
async def reset_password(session: AsyncSession, email: str, code: str, new_password: str) -> None:
    user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user is None:
        raise AppError("invalid_code", 400, "The reset code is not valid.")
    request = await session.scalar(
        select(PasswordResetRequest)
        .where(PasswordResetRequest.user_id == user.user_id, PasswordResetRequest.used.is_(False))
        .order_by(PasswordResetRequest.expires_at.desc())
    )
    if (
        request is None
        or request.expires_at is None
        or request.expires_at < _now()
        or not request.token_hash
        or not otp_matches(code, request.token_hash)
    ):
        raise AppError("invalid_code", 400, "The reset code is not valid.")
    request.used = True
    user.password_hash = hash_password(new_password)
    await session.execute(
        update(AuthToken)
        .where(AuthToken.user_id == user.user_id, AuthToken.token_type == "refresh")
        .values(revoked=True)
    )
    await session.execute(
        update(LoginSession)
        .where(LoginSession.user_id == user.user_id, LoginSession.status == "active")
        .values(status="ended", ended_at=_now())
    )
    await session.commit()


# يرسل طلب ربط الوصي إلى المريض المحدد.
async def request_guardian_link(
    session: AsyncSession,
    guardian: GuardianProfile,
    actor: User,
    patient_email: str | None,
    national_id: str | None,
) -> dict:
    patient = await _find_patient(session, patient_email, national_id)
    if patient is None:
        raise AppError("patient_not_found", 404, "No patient matched those details.")
    existing = await session.scalar(
        select(PatientGuardianLink).where(
            PatientGuardianLink.patient_id == patient.patient_id,
            PatientGuardianLink.guardian_id == guardian.guardian_id,
        )
    )
    if existing and existing.link_status in {"pending", "approved"}:
        raise AppError("link_exists", 409, "A link request already exists.")
    now = _now()
    if existing:
        existing.link_status = "pending"
        existing.requested_at = now
        existing.approved_at = None
        link = existing
    else:
        link = PatientGuardianLink(
            patient_id=patient.patient_id,
            guardian_id=guardian.guardian_id,
            link_status="pending",
            requested_at=now,
        )
        session.add(link)
        await session.flush()
    patient_user = await session.get(User, patient.user_id)
    if patient_user:
        locale = patient_user.preferred_locale or "ar"
        title = "طلب ربط من الوصي" if locale == "ar" else "Guardian link request"
        body = (
            f"{actor.full_name} يطلب الارتباط بملفك الصحي."
            if locale == "ar"
            else f"{actor.full_name} asked to follow your care."
        )
        await notify_user(session, patient_user.user_id, title, body, "guardian_link", str(link.link_id))
    return {"link_id": link.link_id, "link_status": link.link_status}


# يبحث عن المريض بالبريد أو برقم الهوية.
async def _find_patient(session: AsyncSession, email: str | None, national_id: str | None) -> PatientProfile | None:
    if email:
        user = await session.scalar(select(User).where(func.lower(User.email) == email.lower()))
        if user is None:
            return None
        return await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
    if national_id:
        return await session.scalar(select(PatientProfile).where(PatientProfile.national_id == national_id))
    return None
