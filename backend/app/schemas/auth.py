import re
import uuid
from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, model_validator

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ينظّف البريد ويتحقق من صيغته.
def _email(value: str) -> str:
    cleaned = value.strip().lower()
    if not _EMAIL.match(cleaned):
        raise ValueError("Enter a valid email address.")
    return cleaned


EmailAddress = Annotated[str, AfterValidator(_email)]


class PatientOnboarding(BaseModel):
    birth_date: date
    gender: str = Field(min_length=1, max_length=32)
    national_id: str | None = Field(default=None, max_length=64)
    occupation: str | None = Field(default=None, max_length=120)
    work_posture_notes: str | None = Field(default=None, max_length=1000)
    health_condition: str = Field(min_length=2, max_length=500)
    pain_level: int = Field(ge=0, le=10)
    medical_history: str | None = Field(default=None, max_length=4000)


class DoctorOnboarding(BaseModel):
    medical_title: str = Field(min_length=2, max_length=120)
    specialization: str = Field(min_length=2, max_length=160)
    years_of_experience: int = Field(ge=0, le=80)
    clinic_name: str | None = Field(default=None, max_length=160)
    license_number: str = Field(min_length=3, max_length=80)
    issuing_authority: str = Field(min_length=2, max_length=160)
    issue_date: date | None = None
    expiry_date: date | None = None


class GuardianOnboarding(BaseModel):
    relationship_type: str = Field(min_length=2, max_length=80)
    emergency_contact: bool = True
    patient_email: EmailAddress | None = None


class RegisterRequest(BaseModel):
    role: str
    email: EmailAddress
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    locale: str = "ar"
    accepted_privacy: bool
    patient: PatientOnboarding | None = None
    doctor: DoctorOnboarding | None = None
    guardian: GuardianOnboarding | None = None

    # يتأكد أن التسجيل يحمل بيانات الدور المختار وموافقة الخصوصية.
    @model_validator(mode="after")
    def role_payload(self) -> "RegisterRequest":
        if self.role not in {"patient", "doctor", "guardian"}:
            raise ValueError("role must be patient, doctor, or guardian")
        if not self.accepted_privacy:
            raise ValueError("privacy policy must be accepted")
        if self.locale not in {"ar", "en"}:
            raise ValueError("locale must be ar or en")
        payload = {"patient": self.patient, "doctor": self.doctor, "guardian": self.guardian}[self.role]
        if payload is None:
            raise ValueError(f"{self.role} details are required")
        return self


class LoginRequest(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=1, max_length=72)
    role: str | None = None


class OtpRequest(BaseModel):
    email: EmailAddress
    code: str = Field(min_length=6, max_length=6)


class ResendOtpRequest(BaseModel):
    email: EmailAddress
    purpose: str = "verify"


class ForgotPasswordRequest(BaseModel):
    email: EmailAddress


class ResetPasswordRequest(BaseModel):
    email: EmailAddress
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=72)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str
    code: str | None = None


class ProfilePatch(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    preferred_locale: str | None = None
    occupation: str | None = None
    work_posture_notes: str | None = None
    primary_language: str | None = None
    medical_title: str | None = None
    clinic_name: str | None = None
    specialization: str | None = None
    years_of_experience: int | None = Field(default=None, ge=0, le=80)
    relationship_type: str | None = None
    emergency_contact: bool | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class PreferencePatch(BaseModel):
    medical_alerts_enabled: bool | None = None
    session_reminders_enabled: bool | None = None
    emergency_alerts_enabled: bool | None = None
    channel_preference: str | None = None
    community_share_enabled: bool | None = None


class LinkDecision(BaseModel):
    decision: str


class GuardianLinkRequest(BaseModel):
    patient_email: EmailAddress | None = None
    national_id: str | None = None

    # يشترط إدخال البريد أو رقم الهوية عند طلب الربط.
    @model_validator(mode="after")
    def one_identifier(self) -> "GuardianLinkRequest":
        if not self.patient_email and not self.national_id:
            raise ValueError("patient email or national id is required")
        return self


class BanRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
    lifts_at: datetime | None = None


class LicenseDecision(BaseModel):
    decision: str
    notes: str | None = Field(default=None, max_length=2000)


class UserPublic(BaseModel):
    user_id: uuid.UUID
    email: str
    phone: str | None
    full_name: str
    account_status: str
    email_verified: bool
    preferred_locale: str
    avatar_uri: str | None
    roles: list[str]
    created_at: datetime | None
    last_login_at: datetime | None
    profile: dict


class SessionPublic(BaseModel):
    session_id: uuid.UUID
    device_label: str
    ip_address: str | None
    status: str | None
    started_at: datetime | None
    ended_at: datetime | None


class NotificationPublic(BaseModel):
    notification_id: uuid.UUID
    title: str | None
    body: str | None
    priority: str | None
    read_flag: bool
    created_at: datetime | None
    kind: str | None = None
    link_id: uuid.UUID | None = None


class LinkPublic(BaseModel):
    link_id: uuid.UUID
    link_status: str | None
    requested_at: datetime | None
    approved_at: datetime | None
    patient_name: str | None = None
    guardian_name: str | None = None
    relationship_type: str | None = None
