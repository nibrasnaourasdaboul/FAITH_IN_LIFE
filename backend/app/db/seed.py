from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import (
    AdminProfile,
    ConsentPolicy,
    NotificationPreference,
    Permission,
    PrivacyConsent,
    Role,
    RolePermission,
    User,
    UserRole,
)
from datetime import datetime, timezone

ROLE_PERMISSIONS = {
    "patient": {
        "name": "Patient",
        "description": "Person receiving remote rehabilitation",
        "permissions": ["profile.self", "guardian.review", "consents.manage"],
    },
    "doctor": {
        "name": "Physical therapist / doctor",
        "description": "Clinician who assesses, prescribes, and follows care",
        "permissions": ["profile.self", "patients.read", "license.submit", "consents.manage"],
    },
    "guardian": {
        "name": "Guardian",
        "description": "Family member or guardian linked to a patient",
        "permissions": ["profile.self", "guardian.link", "consents.manage"],
    },
    "admin": {
        "name": "Administrator",
        "description": "Operates governance, licenses, and account safety",
        "permissions": ["profile.self", "accounts.manage", "licenses.review", "audit.read", "consents.manage"],
    },
}

PERMISSIONS = {
    "profile.self": "View and edit the signed-in profile",
    "guardian.review": "Approve or reject guardian links",
    "guardian.link": "Request a link to a patient",
    "consents.manage": "Manage privacy and notification consents",
    "patients.read": "Read assigned patient summaries",
    "license.submit": "Submit a professional license",
    "accounts.manage": "Suspend, restore, and review accounts",
    "licenses.review": "Approve or reject clinician licenses",
    "audit.read": "Read audit and access logs",
}


# يجهّز الأدوار والصلاحيات وحساب المدير، ويحوّل دور المرافق القديم إلى الوصي.
async def seed(session: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    legacy_role = await session.scalar(select(Role).where(Role.role_code == "caregiver"))
    if legacy_role is not None:
        legacy_role.role_code = "guardian"
    for old_code, new_code in {"caregiver.review": "guardian.review", "caregiver.link": "guardian.link"}.items():
        legacy_permission = await session.scalar(select(Permission).where(Permission.permission_code == old_code))
        if legacy_permission is not None:
            legacy_permission.permission_code = new_code
    permission_rows: dict[str, Permission] = {}
    for code, description in PERMISSIONS.items():
        row = await session.scalar(select(Permission).where(Permission.permission_code == code))
        if row is None:
            row = Permission(permission_code=code, description=description)
            session.add(row)
            await session.flush()
        else:
            row.description = description
        permission_rows[code] = row

    for code, meta in ROLE_PERMISSIONS.items():
        role = await session.scalar(select(Role).where(Role.role_code == code))
        if role is None:
            role = Role(role_code=code, role_name=meta["name"], description=meta["description"])
            session.add(role)
            await session.flush()
        else:
            role.role_name = meta["name"]
            role.description = meta["description"]
        for perm_code in meta["permissions"]:
            exists = await session.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id == permission_rows[perm_code].permission_id,
                )
            )
            if exists is None:
                session.add(
                    RolePermission(
                        role_id=role.role_id,
                        permission_id=permission_rows[perm_code].permission_id,
                    )
                )

    policy = await session.scalar(select(ConsentPolicy).where(ConsentPolicy.policy_code == "privacy"))
    if policy is None:
        session.add(
            ConsentPolicy(
                policy_code="privacy",
                version="1.0",
                content_uri="/privacy",
                effective_from=now,
            )
        )

    settings = get_settings()
    admin = await session.scalar(select(User).where(User.email == settings.admin_email.lower()))
    if admin is None:
        admin = User(
            email=settings.admin_email.lower(),
            full_name=settings.admin_name,
            password_hash=hash_password(settings.admin_password),
            account_status="active",
            mfa_enabled=False,
            created_at=now,
            email_verified=True,
            preferred_locale="ar",
        )
        session.add(admin)
        await session.flush()
        role = await session.scalar(select(Role).where(Role.role_code == "admin"))
        session.add(UserRole(user_id=admin.user_id, role_id=role.role_id, assigned_at=now))
        session.add(
            AdminProfile(user_id=admin.user_id)
        )
        session.add(
            NotificationPreference(
                user_id=admin.user_id,
                medical_alerts_enabled=True,
                session_reminders_enabled=True,
                emergency_alerts_enabled=True,
                channel_preference="email",
            )
        )
        policy = await session.scalar(select(ConsentPolicy).where(ConsentPolicy.policy_code == "privacy"))
        if policy:
            session.add(
                PrivacyConsent(
                    user_id=admin.user_id,
                    policy_id=policy.policy_id,
                    consent_scope="account",
                    accepted=True,
                    accepted_at=now,
                )
            )
    await session.commit()
