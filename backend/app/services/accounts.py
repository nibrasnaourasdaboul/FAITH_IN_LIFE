import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models import (
    AdminProfile,
    AuthToken,
    CareEpisode,
    CommunityShareConsent,
    DoctorProfile,
    GuardianProfile,
    LicenseCredential,
    LicenseReview,
    LoginSession,
    MedicalRecord,
    Notification,
    NotificationPreference,
    PatientGuardianLink,
    PatientProfile,
    Role,
    SpecialtyExpertise,
    User,
    UserBanRecord,
    UserNotificationState,
    UserRole,
)
from app.services.identity import build_profile, public_user, request_guardian_link
from app.services.notifications import notify_user
from app.services.storage import storage


# يُرجع الوقت الحالي بالتوقيت العالمي.
def _now() -> datetime:
    return datetime.now(timezone.utc)


# يحفظ تعديلات الملف الشخصي حسب دور المستخدم.
async def update_profile(session: AsyncSession, user: User, data) -> dict:
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.phone is not None:
        user.phone = data.phone
    if data.preferred_locale is not None:
        if data.preferred_locale not in {"ar", "en"}:
            raise AppError("invalid_locale", 422, "Locale must be ar or en.")
        user.preferred_locale = data.preferred_locale
        patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
        if patient and data.primary_language is None:
            patient.primary_language = data.preferred_locale

    patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
    if patient:
        if data.occupation is not None:
            patient.occupation = data.occupation
        if data.work_posture_notes is not None:
            patient.work_posture_notes = data.work_posture_notes
        if data.primary_language is not None:
            patient.primary_language = data.primary_language

    doctor = await session.scalar(select(DoctorProfile).where(DoctorProfile.user_id == user.user_id))
    if doctor:
        if data.medical_title is not None:
            doctor.medical_title = data.medical_title
        if data.clinic_name is not None:
            doctor.clinic_name = data.clinic_name
        if data.specialization is not None:
            doctor.specialization = data.specialization
            expertise = await session.scalar(select(SpecialtyExpertise).where(SpecialtyExpertise.doctor_id == doctor.doctor_id))
            if expertise:
                expertise.specialty_name = data.specialization
        if data.years_of_experience is not None:
            doctor.years_of_experience = data.years_of_experience

    guardian = await session.scalar(select(GuardianProfile).where(GuardianProfile.user_id == user.user_id))
    if guardian:
        if data.relationship_type is not None:
            guardian.relationship_type = data.relationship_type
        if data.emergency_contact is not None:
            guardian.emergency_contact = data.emergency_contact

    await session.commit()
    await session.refresh(user)
    profile = await build_profile(session, user)
    return public_user(user, profile)


# يستبدل كلمة المرور بعد مطابقة الحالية.
async def change_password(session: AsyncSession, user: User, current: str, new_password: str) -> None:
    if not user.password_hash or not verify_password(current, user.password_hash):
        raise AppError("invalid_password", 400, "Current password is incorrect.")
    user.password_hash = hash_password(new_password)
    await session.commit()


# يخزّن صورة الحساب ويربطها بالمستخدم.
async def save_avatar(session: AsyncSession, user: User, filename: str, data: bytes, content_type: str) -> dict:
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise AppError("invalid_file", 400, "Avatar must be a JPEG, PNG, or WebP image.")
    if len(data) > 2_000_000:
        raise AppError("file_too_large", 400, "Avatar must be smaller than 2 MB.")
    user.avatar_uri = storage.save_bytes("avatars", filename, data, content_type)
    await session.commit()
    profile = await build_profile(session, user)
    return public_user(user, profile)


# يحفظ تفضيلات التنبيهات ومشاركة المجتمع.
async def update_preferences(session: AsyncSession, user: User, data) -> dict:
    prefs = await session.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user.user_id))
    if prefs is None:
        prefs = NotificationPreference(user_id=user.user_id)
        session.add(prefs)
    if data.medical_alerts_enabled is not None:
        prefs.medical_alerts_enabled = data.medical_alerts_enabled
    if data.session_reminders_enabled is not None:
        prefs.session_reminders_enabled = data.session_reminders_enabled
    if data.emergency_alerts_enabled is not None:
        prefs.emergency_alerts_enabled = data.emergency_alerts_enabled
    if data.channel_preference is not None:
        prefs.channel_preference = data.channel_preference

    if data.community_share_enabled is not None:
        patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
        if patient is None:
            raise AppError("not_patient", 403, "Only a patient can change community sharing.")
        record = await session.scalar(
            select(MedicalRecord)
            .join(CareEpisode, CareEpisode.episode_id == MedicalRecord.episode_id)
            .where(CareEpisode.patient_id == patient.patient_id)
        )
        if record is None:
            raise AppError("record_missing", 409, "Medical record is not ready yet.")
        consent = await session.scalar(
            select(CommunityShareConsent).where(CommunityShareConsent.record_id == record.record_id)
        )
        now = _now()
        if consent is None:
            session.add(
                CommunityShareConsent(
                    record_id=record.record_id,
                    patient_id=patient.patient_id,
                    anonymized=True,
                    status="approved" if data.community_share_enabled else "revoked",
                    approved_at=now if data.community_share_enabled else None,
                    revoked_at=None if data.community_share_enabled else now,
                )
            )
        else:
            consent.status = "approved" if data.community_share_enabled else "revoked"
            consent.anonymized = True
            if data.community_share_enabled:
                consent.approved_at = now
                consent.revoked_at = None
            else:
                consent.revoked_at = now
    await session.commit()
    return await build_profile(session, user)


# يجمع الجلسات النشطة لهذا الحساب.
async def list_sessions(session: AsyncSession, user: User) -> list[dict]:
    rows = await session.scalars(
        select(LoginSession).where(LoginSession.user_id == user.user_id).order_by(LoginSession.started_at.desc())
    )
    items = []
    for row in rows:
        try:
            label = json.loads(row.device_info or "{}").get("user_agent", "Unknown device")
        except json.JSONDecodeError:
            label = "Unknown device"
        items.append(
            {
                "session_id": row.session_id,
                "device_label": label,
                "ip_address": row.ip_address,
                "status": row.status,
                "started_at": row.started_at,
                "ended_at": row.ended_at,
            }
        )
    return items


# يغلق جلسة واحدة ويلغي رموزها.
async def revoke_session(session: AsyncSession, user: User, session_id: uuid.UUID) -> None:
    row = await session.get(LoginSession, session_id)
    if row is None or row.user_id != user.user_id:
        raise AppError("not_found", 404, "Session was not found.")
    row.status = "ended"
    row.ended_at = _now()
    try:
        digest = json.loads(row.device_info or "{}").get("refresh_hash")
    except json.JSONDecodeError:
        digest = None
    if digest:
        await session.execute(update(AuthToken).where(AuthToken.token_hash == digest).values(revoked=True))
    await session.commit()


# يجمع إشعارات المستخدم مع حالة القراءة.
async def list_notifications(session: AsyncSession, user: User) -> list[dict]:
    result = await session.execute(
        select(Notification, UserNotificationState)
        .join(UserNotificationState, UserNotificationState.notification_id == Notification.notification_id)
        .where(UserNotificationState.user_id == user.user_id, UserNotificationState.archived.is_(False))
        .order_by(Notification.publish_at.desc())
    )
    items = []
    for note, state in result.all():
        link_id = None
        if note.dedupe_key:
            try:
                link_id = uuid.UUID(note.dedupe_key)
            except ValueError:
                link_id = None
        items.append(
            {
                "notification_id": note.notification_id,
                "title": note.title,
                "body": note.body,
                "priority": note.priority,
                "read_flag": bool(state.read_flag),
                "created_at": note.publish_at,
                "kind": note.notification_type,
                "link_id": link_id,
            }
        )
    return items


# يسجّل أن المستخدم قرأ الإشعار.
async def mark_notification_read(session: AsyncSession, user: User, notification_id: uuid.UUID) -> None:
    state = await session.scalar(
        select(UserNotificationState).where(
            UserNotificationState.user_id == user.user_id,
            UserNotificationState.notification_id == notification_id,
        )
    )
    if state is None:
        raise AppError("not_found", 404, "Notification was not found.")
    state.read_flag = True
    state.read_at = _now()
    await session.commit()


# ينشئ طلب ربط من حساب الوصي إلى المريض.
async def guardian_request(session: AsyncSession, user: User, patient_email: str | None, national_id: str | None) -> dict:
    guardian = await session.scalar(select(GuardianProfile).where(GuardianProfile.user_id == user.user_id))
    if guardian is None:
        raise AppError("not_guardian", 403, "Only a guardian can request a patient link.")
    payload = await request_guardian_link(session, guardian, user, patient_email, national_id)
    await session.commit()
    return payload


# يعرض روابط الوصي سواء للمريض أو للوصي.
async def list_links(session: AsyncSession, user: User) -> list[dict]:
    roles = await session.scalars(
        select(Role.role_code).join(UserRole, UserRole.role_id == Role.role_id).where(UserRole.user_id == user.user_id)
    )
    codes = set(roles.all())
    items: list[dict] = []
    if "patient" in codes:
        patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
        if patient:
            rows = await session.execute(
                select(PatientGuardianLink, GuardianProfile, User)
                .join(GuardianProfile, GuardianProfile.guardian_id == PatientGuardianLink.guardian_id)
                .join(User, User.user_id == GuardianProfile.user_id)
                .where(PatientGuardianLink.patient_id == patient.patient_id)
                .order_by(PatientGuardianLink.requested_at.desc())
            )
            for link, profile, guardian_user in rows.all():
                items.append(_link_dict(link, patient_name=user.full_name, guardian_name=guardian_user.full_name, relationship=profile.relationship_type))
    if "guardian" in codes:
        guardian = await session.scalar(select(GuardianProfile).where(GuardianProfile.user_id == user.user_id))
        if guardian:
            rows = await session.execute(
                select(PatientGuardianLink, PatientProfile, User)
                .join(PatientProfile, PatientProfile.patient_id == PatientGuardianLink.patient_id)
                .join(User, User.user_id == PatientProfile.user_id)
                .where(PatientGuardianLink.guardian_id == guardian.guardian_id)
                .order_by(PatientGuardianLink.requested_at.desc())
            )
            for link, _patient, patient_user in rows.all():
                items.append(
                    _link_dict(link, patient_name=patient_user.full_name, guardian_name=user.full_name, relationship=guardian.relationship_type)
                )
    return items


# يرتّب بيانات طلب الربط لعرضها في الواجهة.
def _link_dict(link, patient_name, guardian_name, relationship) -> dict:
    return {
        "link_id": link.link_id,
        "link_status": link.link_status,
        "requested_at": link.requested_at,
        "approved_at": link.approved_at,
        "patient_name": patient_name,
        "guardian_name": guardian_name,
        "relationship_type": relationship,
    }


# يحفظ موافقة المريض أو رفضه ويخبر الوصي.
async def decide_link(session: AsyncSession, user: User, link_id: uuid.UUID, decision: str) -> dict:
    if decision not in {"approved", "rejected"}:
        raise AppError("invalid_decision", 422, "Decision must be approved or rejected.")
    patient = await session.scalar(select(PatientProfile).where(PatientProfile.user_id == user.user_id))
    if patient is None:
        raise AppError("not_patient", 403, "Only the patient can decide a guardian link.")
    link = await session.get(PatientGuardianLink, link_id)
    if link is None or link.patient_id != patient.patient_id:
        raise AppError("not_found", 404, "Link request was not found.")
    if link.link_status != "pending":
        raise AppError("already_decided", 409, "This request was already decided.")
    link.link_status = decision
    if decision == "approved":
        link.approved_at = _now()
    profile = await session.get(GuardianProfile, link.guardian_id)
    guardian_user = await session.get(User, profile.user_id) if profile else None
    if guardian_user:
        locale = guardian_user.preferred_locale or "ar"
        approved = decision == "approved"
        title = ("تمت الموافقة على الربط" if approved else "تم رفض طلب الربط") if locale == "ar" else (
            "Link approved" if approved else "Link declined"
        )
        body = (
            f"{user.full_name} {'وافق على' if approved else 'رفض'} طلب المتابعة."
            if locale == "ar"
            else f"{user.full_name} {'approved' if approved else 'declined'} the follow request."
        )
        await notify_user(session, guardian_user.user_id, title, body, "guardian_link_decision", str(link.link_id))
    await session.commit()
    return _link_dict(link, user.full_name, guardian_user.full_name if guardian_user else None, profile.relationship_type if profile else None)


# يبحث في الحسابات لشاشة المدير.
async def admin_users(session: AsyncSession, query: str | None, role: str | None) -> list[dict]:
    stmt = select(User).order_by(User.created_at.desc())
    if query:
        like = f"%{query.lower()}%"
        stmt = stmt.where(or_(func.lower(User.full_name).like(like), func.lower(User.email).like(like)))
    users = (await session.scalars(stmt.limit(100))).all()
    items = []
    for user in users:
        profile = await build_profile(session, user)
        if role and role not in profile.get("roles", []):
            continue
        items.append(public_user(user, profile))
    return items


# يعلّق الحساب ويسجّل سبب الإيقاف.
async def ban_user(session: AsyncSession, actor: User, user_id: uuid.UUID, reason: str, lifts_at: datetime | None) -> None:
    if actor.user_id == user_id:
        raise AppError("cannot_ban_self", 400, "You cannot suspend your own account.")
    target = await session.get(User, user_id)
    if target is None:
        raise AppError("not_found", 404, "User was not found.")
    admin = await session.scalar(select(AdminProfile).where(AdminProfile.user_id == actor.user_id))
    target.account_status = "banned"
    session.add(
        UserBanRecord(
            user_id=target.user_id,
            banned_by_admin_id=admin.admin_id if admin else None,
            reason=reason,
            banned_at=_now(),
            lifts_at=lifts_at,
            status="active",
        )
    )
    await session.execute(update(AuthToken).where(AuthToken.user_id == target.user_id).values(revoked=True))
    await session.execute(
        update(LoginSession)
        .where(LoginSession.user_id == target.user_id, LoginSession.status == "active")
        .values(status="ended", ended_at=_now())
    )
    await session.commit()


# يعيد الحساب إلى الحالة النشطة.
async def unban_user(session: AsyncSession, user_id: uuid.UUID) -> None:
    target = await session.get(User, user_id)
    if target is None:
        raise AppError("not_found", 404, "User was not found.")
    target.account_status = "active" if target.email_verified else "pending_verification"
    bans = await session.scalars(select(UserBanRecord).where(UserBanRecord.user_id == user_id, UserBanRecord.status == "active"))
    for ban in bans:
        ban.status = "lifted"
    await session.commit()


# يجمع التراخيص التي لم تُراجع بعد.
async def pending_licenses(session: AsyncSession) -> list[dict]:
    rows = await session.execute(
        select(LicenseCredential, DoctorProfile, User)
        .join(DoctorProfile, DoctorProfile.doctor_id == LicenseCredential.doctor_id)
        .join(User, User.user_id == DoctorProfile.user_id)
        .where(LicenseCredential.status == "pending")
        .order_by(User.created_at.desc())
    )
    return [
        {
            "license_id": lic.license_id,
            "license_number": lic.license_number,
            "issuing_authority": lic.issuing_authority,
            "issue_date": lic.issue_date,
            "expiry_date": lic.expiry_date,
            "status": lic.status,
            "doctor_name": user.full_name,
            "email": user.email,
            "medical_title": doctor.medical_title,
        }
        for lic, doctor, user in rows.all()
    ]


# يحفظ قرار مراجعة الترخيص ويحدّث حالة الطبيب.
async def review_license(session: AsyncSession, actor: User, license_id: uuid.UUID, decision: str, notes: str | None) -> None:
    if decision not in {"approved", "rejected"}:
        raise AppError("invalid_decision", 422, "Decision must be approved or rejected.")
    lic = await session.get(LicenseCredential, license_id)
    if lic is None:
        raise AppError("not_found", 404, "License was not found.")
    admin = await session.scalar(select(AdminProfile).where(AdminProfile.user_id == actor.user_id))
    if admin is None:
        raise AppError("not_admin", 403, "Admin profile is required.")
    lic.status = decision
    doctor = await session.get(DoctorProfile, lic.doctor_id) if lic.doctor_id else None
    if doctor:
        doctor.is_verified = decision == "approved"
        doctor.is_available = decision == "approved"
        owner = await session.get(User, doctor.user_id)
        if owner:
            locale = owner.preferred_locale or "ar"
            title = "نتيجة مراجعة الترخيص" if locale == "ar" else "License review result"
            body = (
                "تم اعتماد ترخيصك المهني." if decision == "approved" else "لم يتم اعتماد الترخيص. راجع البيانات وأعد الإرسال."
            ) if locale == "ar" else (
                "Your professional license was approved." if decision == "approved" else "Your license was not approved."
            )
            await notify_user(session, owner.user_id, title, body, "license_review", str(lic.license_id))
    session.add(
        LicenseReview(
            license_id=lic.license_id,
            admin_id=admin.admin_id,
            decision=decision,
            notes=notes,
            reviewed_at=_now(),
        )
    )
    await session.commit()
