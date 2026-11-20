"""SQLAlchemy models generated from FAITH in LIFE Diagrams/ERD ER Diagram/FAITH_in_LIFE_ERD.dbml.

Do not edit by hand. Regenerate with backend/scripts/generate_models.py.
User gains email verification, locale, and avatar fields required by the
account-management flows. EmbeddingIndex.embedding is JSON because
pgvector is not installed on this PostgreSQL server.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_status: Mapped[str] = mapped_column(String(255), nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_locale: Mapped[str] = mapped_column(String(8), default="ar", nullable=False)
    avatar_uri: Mapped[str | None] = mapped_column(Text, nullable=True)


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    role_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    permission_code: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),)

    user_role_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    role_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"),)

    role_permission_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    role_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=True, index=True)
    permission_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("permissions.permission_id", ondelete="CASCADE"), nullable=True, index=True)


class LoginSession(Base):
    __tablename__ = "login_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    attempt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    success: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    ip_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    token_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    token_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(255), nullable=True)
    national_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    occupation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_posture_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_language: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    professional_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    medical_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clinic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    is_available: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class GuardianProfile(Base):
    __tablename__ = "guardian_profiles"

    guardian_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    relationship_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    admin_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)


class UserBanRecord(Base):
    __tablename__ = "user_ban_records"

    ban_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    banned_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    banned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lifts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"

    reset_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class ConsentPolicy(Base):
    __tablename__ = "consent_policies"

    policy_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    policy_code: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PrivacyConsent(Base):
    __tablename__ = "privacy_consents"

    consent_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    policy_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("consent_policies.policy_id", ondelete="CASCADE"), nullable=True, index=True)
    consent_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    medical_alerts_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    session_reminders_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    emergency_alerts_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    channel_preference: Mapped[str | None] = mapped_column(String(255), nullable=True)


class LicenseCredential(Base):
    __tablename__ = "license_credentials"

    license_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    license_number: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class LicenseReview(Base):
    __tablename__ = "license_reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    license_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("license_credentials.license_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    decision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SpecialtyExpertise(Base):
    __tablename__ = "specialty_expertises"

    expertise_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    specialty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expertise_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certification_uri: Mapped[str | None] = mapped_column(Text, nullable=True)


class PatientGuardianLink(Base):
    __tablename__ = "patient_guardian_links"
    __table_args__ = (UniqueConstraint("patient_id", "guardian_id", name="uq_patient_guardian_links_patient_id_guardian_id"),)

    link_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    link_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CareEpisode(Base):
    __tablename__ = "care_episodes"

    episode_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    injury_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opened_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_on: Mapped[date | None] = mapped_column(Date, nullable=True)


class Diagnosis(Base):
    __tablename__ = "diagnosises"

    diagnosis_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    diagnosis_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnosis_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnosed_on: Mapped[date | None] = mapped_column(Date, nullable=True)


class CaseStatusHistory(Base):
    __tablename__ = "case_status_histories"

    history_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    from_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_by_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CareAssignment(Base):
    __tablename__ = "care_assignments"

    assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    care_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assignment_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_primary: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class DoctorChangeRequest(Base):
    __tablename__ = "doctor_change_requests"

    change_request_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    current_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    requested_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClinicalComplaint(Base):
    __tablename__ = "clinical_complaints"

    complaint_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    onset_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class TriageResult(Base):
    __tablename__ = "triage_results"

    triage_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_complaints.complaint_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    urgency_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggested_specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    triaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)


class UnassignedCase(Base):
    __tablename__ = "unassigned_cases"

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_complaints.complaint_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    priority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    queue_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CaseAssignment(Base):
    __tablename__ = "case_assignments"

    case_assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("unassigned_cases.case_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    assignment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DoctorCandidateReview(Base):
    __tablename__ = "doctor_candidate_reviews"

    candidate_review_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    match_score: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    record_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    record_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    encryption_status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DemographicProfile(Base):
    __tablename__ = "demographic_profiles"

    demographic_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class MedicalHistoryEntry(Base):
    __tablename__ = "medical_history_entries"

    history_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    history_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ChronicCondition(Base):
    __tablename__ = "chronic_conditions"

    condition_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    condition_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnosed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    management_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ClinicalDocument(Base):
    __tablename__ = "clinical_documents"

    document_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    author_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    document_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImagingStudy(Base):
    __tablename__ = "imaging_studies"

    study_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    modality: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body_region: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImagingSeries(Base):
    __tablename__ = "imaging_serieses"

    series_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    study_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("imaging_studies.study_id", ondelete="CASCADE"), nullable=True, index=True)
    series_uid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instance_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ImagingInstance(Base):
    __tablename__ = "imaging_instances"

    instance_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    series_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("imaging_serieses.series_id", ondelete="CASCADE"), nullable=True, index=True)
    file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("stored_files.file_id", ondelete="CASCADE"), nullable=True, index=True)
    sop_instance_uid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    frame_number: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ImagingQualityCheck(Base):
    __tablename__ = "imaging_quality_checks"

    quality_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    study_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("imaging_studies.study_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    quality_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issues: Mapped[str | None] = mapped_column(String(255), nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClinicalInterpretation(Base):
    __tablename__ = "clinical_interpretations"

    interpretation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    study_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("imaging_studies.study_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    impression: Mapped[str | None] = mapped_column(Text, nullable=True)
    interpreted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SimplifiedExplanation(Base):
    __tablename__ = "simplified_explanations"

    explanation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    interpretation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_interpretations.interpretation_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    plain_language_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_aid_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RecordShareRequest(Base):
    __tablename__ = "record_share_requests"

    share_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    requester_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    consent_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ShareRecipient(Base):
    __tablename__ = "share_recipients"

    share_recipient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    share_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("record_share_requests.share_id", ondelete="CASCADE"), nullable=True, index=True)
    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    access_level: Mapped[str | None] = mapped_column(String(255), nullable=True)


class RecordShareItem(Base):
    __tablename__ = "record_share_items"

    share_item_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    share_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("record_share_requests.share_id", ondelete="CASCADE"), nullable=True, index=True)
    item_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    item_ref_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)


class ReferralSummary(Base):
    __tablename__ = "referral_summaries"

    summary_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    share_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("record_share_requests.share_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    generated_by_ai_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctor_edits: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CommunityShareConsent(Base):
    __tablename__ = "community_share_consents"

    community_consent_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    anonymized: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AnonymizedCaseSnapshot(Base):
    __tablename__ = "anonymized_case_snapshots"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    community_consent_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("community_share_consents.community_consent_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    snapshot_payload_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    created_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_joints: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggested_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    performance_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    publish_status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ExerciseMedia(Base):
    __tablename__ = "exercise_medias"

    media_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("stored_files.file_id", ondelete="CASCADE"), nullable=True, index=True)
    media_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guidance_mode: Mapped[str | None] = mapped_column(Text, nullable=True)


class ExerciseCategory(Base):
    __tablename__ = "exercise_categories"

    category_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    category_name: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class ExerciseCategoryLink(Base):
    __tablename__ = "exercise_category_links"
    __table_args__ = (UniqueConstraint("exercise_id", "category_id", name="uq_exercise_category_links_exercise_id_category_id"),)

    link_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercise_categories.category_id", ondelete="CASCADE"), nullable=True, index=True)


class SafeAngularRange(Base):
    __tablename__ = "safe_angular_ranges"

    range_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    joint_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    min_angle_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_angle_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Contraindication(Base):
    __tablename__ = "contraindications"

    contraindication_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    condition_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guidance: Mapped[str | None] = mapped_column(Text, nullable=True)


class ClinicalProtocol(Base):
    __tablename__ = "clinical_protocols"

    protocol_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    approved_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RehabilitationPlan(Base):
    __tablename__ = "rehabilitation_plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    protocol_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_protocols.protocol_id", ondelete="CASCADE"), nullable=True, index=True)
    plan_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    goals: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    generated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    approval_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PlanExercise(Base):
    __tablename__ = "plan_exercises"

    plan_exercise_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehabilitation_plans.plan_id", ondelete="CASCADE"), nullable=True, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    sets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    intensity_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence_order: Mapped[int | None] = mapped_column(Integer, nullable=True)


class PlanRevision(Base):
    __tablename__ = "plan_revisions"

    revision_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehabilitation_plans.plan_id", ondelete="CASCADE"), nullable=True, index=True)
    revised_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    revision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changes_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    revised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    proposed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    approval_status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ProviderAvailability(Base):
    __tablename__ = "provider_availabilities"

    availability_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    weekday: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    slot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    availability_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("provider_availabilities.availability_id", ondelete="CASCADE"), nullable=True, index=True)
    slot_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slot_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slot_status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    slot_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("appointment_slots.slot_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    appointment_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AppointmentStatusHistory(Base):
    __tablename__ = "appointment_status_histories"

    appt_history_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("appointments.appointment_id", ondelete="CASCADE"), nullable=True, index=True)
    from_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RehabSession(Base):
    __tablename__ = "rehab_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehabilitation_plans.plan_id", ondelete="CASCADE"), nullable=True, index=True)
    plan_exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("plan_exercises.plan_exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    compliance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    requires_guardian: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class SessionAssessment(Base):
    __tablename__ = "session_assessments"

    assessment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    pain_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pain_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fatigue_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    patient_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SessionAttendance(Base):
    __tablename__ = "session_attendances"

    attendance_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    presence_confirmed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SessionReminder(Base):
    __tablename__ = "session_reminders"

    reminder_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)


class CaregiverGuidance(Base):
    __tablename__ = "caregiver_guidances"

    guidance_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=True, index=True)
    plain_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIEngine(Base):
    __tablename__ = "ai_engines"

    ai_engine_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    engine_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operational_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DeviceCaptureSession(Base):
    __tablename__ = "device_capture_sessions"

    capture_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    device_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    tracking_distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    capture_status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class MotionAnalysis(Base):
    __tablename__ = "motion_analysises"

    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    capture_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("device_capture_sessions.capture_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    overall_form_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    completed_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pose_tracking_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smoothing_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MotionSample(Base):
    __tablename__ = "motion_samples"

    sample_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    frame_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sampled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tracking_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    skeleton_payload_uri: Mapped[str | None] = mapped_column(Text, nullable=True)


class JointMeasurement(Base):
    __tablename__ = "joint_measurements"

    measurement_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    joint_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    angle_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_angle_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    rom_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    within_safe_range: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MotionFeedbackEvent(Base):
    __tablename__ = "motion_feedback_events"

    feedback_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    feedback_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_mode: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    emitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VitalSignObservation(Base):
    __tablename__ = "vital_sign_observations"

    vital_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    vital_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vital_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_flag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SafetyIncident(Base):
    __tablename__ = "safety_incidents"

    incident_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    incident_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_signs: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EmergencyStop(Base):
    __tablename__ = "emergency_stops"

    stop_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("safety_incidents.incident_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    session_halted: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    halted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    halt_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class MotionReview(Base):
    __tablename__ = "motion_reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outputs_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    rule_adjustments: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GamificationProfile(Base):
    __tablename__ = "gamification_profiles"

    gamification_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    total_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    streak_days: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RewardPointTx(Base):
    __tablename__ = "reward_point_txes"

    tx_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    gamification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("gamification_profiles.gamification_id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), nullable=True, index=True)
    points_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RewardCatalog(Base):
    __tablename__ = "reward_catalogs"

    reward_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    reward_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    points_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"

    redemption_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    gamification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("gamification_profiles.gamification_id", ondelete="CASCADE"), nullable=True, index=True)
    reward_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("reward_catalogs.reward_id", ondelete="CASCADE"), nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Badge(Base):
    __tablename__ = "badges"

    badge_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    badge_code: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    badge_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criteria: Mapped[str | None] = mapped_column(Text, nullable=True)


class PatientBadge(Base):
    __tablename__ = "patient_badges"
    __table_args__ = (UniqueConstraint("patient_id", "badge_id", name="uq_patient_badges_patient_id_badge_id"),)

    patient_badge_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    badge_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("badges.badge_id", ondelete="CASCADE"), nullable=True, index=True)
    awarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MotivationMessage(Base):
    __tablename__ = "motivation_messages"

    motivation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DailyRecoveryBoard(Base):
    __tablename__ = "daily_recovery_boards"

    board_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    board_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recovery_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)
    points_today: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ClinicalRule(Base):
    __tablename__ = "clinical_rules"

    rule_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    managed_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    rule_code: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    rule_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    activation_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClinicalRuleCondition(Base):
    __tablename__ = "clinical_rule_conditions"

    condition_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_rules.rule_id", ondelete="CASCADE"), nullable=True, index=True)
    metric_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)


class ClinicalRuleAction(Base):
    __tablename__ = "clinical_rule_actions"

    action_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_rules.rule_id", ondelete="CASCADE"), nullable=True, index=True)
    action_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action_payload: Mapped[str | None] = mapped_column(Text, nullable=True)


class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_logs"

    execution_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_rules.rule_id", ondelete="CASCADE"), nullable=True, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    result: Mapped[str | None] = mapped_column(String(255), nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MedicalReference(Base):
    __tablename__ = "medical_references"

    reference_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_rules.rule_id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_trusted: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class ClinicalRuleProposal(Base):
    __tablename__ = "clinical_rule_proposals"

    proposal_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    resulting_rule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_rules.rule_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    proposal_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proposed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIServiceSetting(Base):
    __tablename__ = "ai_service_settings"

    setting_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    error_sensitivity: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_response_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_model_ids: Mapped[str | None] = mapped_column(String(255), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIModelVersion(Base):
    __tablename__ = "ai_model_versions"

    model_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class AIPerformanceMetric(Base):
    __tablename__ = "ai_performance_metrics"

    metric_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    model_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_model_versions.model_id", ondelete="CASCADE"), nullable=True, index=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    measured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIRun(Base):
    __tablename__ = "ai_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    model_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_model_versions.model_id", ondelete="CASCADE"), nullable=True, index=True)
    run_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIRunIO(Base):
    __tablename__ = "ai_run_ios"

    io_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    io_direction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str | None] = mapped_column(Text, nullable=True)


class AIApproval(Base):
    __tablename__ = "ai_approvals"

    approval_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    decision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImagingAIAnalysis(Base):
    __tablename__ = "imaging_ai_analysises"

    imaging_ai_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    study_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("imaging_studies.study_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    preliminary_findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RelapseRiskAnalysis(Base):
    __tablename__ = "relapse_risk_analysises"

    risk_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contributing_factors: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    rag_doc_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_references.reference_id", ondelete="CASCADE"), nullable=True, index=True)
    content_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RAGChunk(Base):
    __tablename__ = "rag_chunks"

    chunk_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    rag_doc_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rag_documents.rag_doc_id", ondelete="CASCADE"), nullable=True, index=True)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_text: Mapped[str | None] = mapped_column(Text, nullable=True)


class EmbeddingIndex(Base):
    __tablename__ = "embedding_indexes"

    embedding_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rag_chunks.chunk_id", ondelete="CASCADE"), nullable=True, index=True)
    vector_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)


class TrustedQAAnswer(Base):
    __tablename__ = "trusted_qa_answers"

    qa_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rag_chunks.chunk_id", ondelete="CASCADE"), nullable=True, index=True)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    template_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    template_code: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    channel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_template: Mapped[str | None] = mapped_column(Text, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notification_templates.template_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audience_filter: Mapped[str | None] = mapped_column(Text, nullable=True)
    schedule_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(255), nullable=True)


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"

    delivery_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    channel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attempt_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserNotificationState(Base):
    __tablename__ = "user_notification_states"

    state_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    read_flag: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class MotorDeclineAlert(Base):
    __tablename__ = "motor_decline_alerts"

    decline_alert_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    metrics_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    threshold_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TherapeuticWarning(Base):
    __tablename__ = "therapeutic_warnings"

    warning_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    warning_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cause_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClinicalEarlyWarning(Base):
    __tablename__ = "clinical_early_warnings"

    early_warning_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    severity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trigger_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    pathway_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IncidentDocumentation(Base):
    __tablename__ = "incident_documentations"

    documentation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    early_warning_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_early_warnings.early_warning_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    clinical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(255), nullable=True)
    documented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class FollowUpNotification(Base):
    __tablename__ = "follow_up_notifications"

    followup_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    followup_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    conversation_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    participant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    participant_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=True, index=True)
    sender_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    message_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_medical_alert: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    attachment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    message_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True, index=True)
    file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("stored_files.file_id", ondelete="CASCADE"), nullable=True, index=True)
    attachment_type: Mapped[str | None] = mapped_column(String(255), nullable=True)


class MessageDelivery(Base):
    __tablename__ = "message_deliveries"

    msg_delivery_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    message_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True, index=True)
    channel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attempt_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MessageReadReceipt(Base):
    __tablename__ = "message_read_receipts"

    receipt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    message_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True, index=True)
    reader_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UrgentContactRequest(Base):
    __tablename__ = "urgent_contact_requests"

    urgent_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    urgency_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EmergencyHelpRequest(Base):
    __tablename__ = "emergency_help_requests"

    help_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("notifications.notification_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    source_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClinicalConsultation(Base):
    __tablename__ = "clinical_consultations"

    consultation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    author_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    community_consent_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("community_share_consents.community_consent_id", ondelete="CASCADE"), nullable=True, index=True)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("anonymized_case_snapshots.snapshot_id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clinical_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ConsultationResponse(Base):
    __tablename__ = "consultation_responses"

    response_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    consultation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_consultations.consultation_id", ondelete="CASCADE"), nullable=True, index=True)
    responder_doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    stance: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ConsultationReport(Base):
    __tablename__ = "consultation_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    reporter_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    report_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SupervisionCase(Base):
    __tablename__ = "supervision_cases"

    supervision_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    consultation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("clinical_consultations.consultation_id", ondelete="CASCADE"), nullable=True, index=True)
    report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("consultation_reports.report_id", ondelete="CASCADE"), nullable=True, index=True)
    case_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SupervisionAction(Base):
    __tablename__ = "supervision_actions"

    action_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    supervision_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("supervision_cases.supervision_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    action_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    acted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ConsultationAppointment(Base):
    __tablename__ = "consultation_appointments"

    consult_appt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("appointments.appointment_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SmartReport(Base):
    __tablename__ = "smart_reports"

    smart_report_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), nullable=True, index=True)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("care_episodes.episode_id", ondelete="CASCADE"), nullable=True, index=True)
    target_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    ai_engine_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_engines.ai_engine_id", ondelete="CASCADE"), nullable=True, index=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ai_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    audience_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    period_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    content_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReportExport(Base):
    __tablename__ = "report_exports"

    export_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    smart_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("smart_reports.smart_report_id", ondelete="CASCADE"), nullable=True, index=True)
    file_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("stored_files.file_id", ondelete="CASCADE"), nullable=True, index=True)
    export_format: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProgressReport(Base):
    __tablename__ = "progress_reports"

    progress_report_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    smart_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("smart_reports.smart_report_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    compliance_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    movement_improvement: Mapped[float | None] = mapped_column(Float, nullable=True)


class DetailedClinicalReport(Base):
    __tablename__ = "detailed_clinical_reports"

    detailed_report_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    smart_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("smart_reports.smart_report_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("doctor_profiles.doctor_id", ondelete="CASCADE"), nullable=True, index=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("motion_analysises.analysis_id", ondelete="CASCADE"), nullable=True, index=True)
    joints_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    errors_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress_curve_uri: Mapped[str | None] = mapped_column(Text, nullable=True)


class WeeklyCareSummary(Base):
    __tablename__ = "weekly_care_summaries"

    weekly_summary_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    smart_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("smart_reports.smart_report_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("guardian_profiles.guardian_id", ondelete="CASCADE"), nullable=True, index=True)
    week_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_sessions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    performance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ReportSession(Base):
    __tablename__ = "report_sessions"
    __table_args__ = (UniqueConstraint("smart_report_id", "session_id", name="uq_report_sessions_smart_report_id_session_id"),)

    report_session_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    smart_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("smart_reports.smart_report_id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rehab_sessions.session_id", ondelete="CASCADE"), nullable=True, index=True)


class StatisticSnapshot(Base):
    __tablename__ = "statistic_snapshots"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_sessions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_compliance: Mapped[float | None] = mapped_column(Float, nullable=True)
    alerts_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    export_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BackupSchedule(Base):
    __tablename__ = "backup_schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    cron_expr: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retention_policy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    backup_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("backup_schedules.schedule_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    backup_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encryption_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BackupIntegrityCheck(Base):
    __tablename__ = "backup_integrity_checks"

    integrity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    backup_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("backup_jobs.backup_id", ondelete="CASCADE"), nullable=True, index=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RestoreOperation(Base):
    __tablename__ = "restore_operations"

    restore_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    backup_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("backup_jobs.backup_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    restore_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RestoreVerification(Base):
    __tablename__ = "restore_verifications"

    verification_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    restore_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("restore_operations.restore_id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    data_consistent: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    audit_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    reviewed_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    action_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditReviewNote(Base):
    __tablename__ = "audit_review_notes"

    note_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    audit_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("audit_log_entries.audit_id", ondelete="CASCADE"), nullable=True, index=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("admin_profiles.admin_id", ondelete="CASCADE"), nullable=True, index=True)
    note_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    protection_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    noted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DataAccessLog(Base):
    __tablename__ = "data_access_logs"

    access_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    record_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("medical_records.record_id", ondelete="CASCADE"), nullable=True, index=True)
    access_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class StoredFile(Base):
    __tablename__ = "stored_files"

    file_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    uploader_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scan_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encryption_key_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


__all__ = [
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "LoginSession",
    "LoginAttempt",
    "AuthToken",
    "PatientProfile",
    "DoctorProfile",
    "GuardianProfile",
    "AdminProfile",
    "UserBanRecord",
    "PasswordResetRequest",
    "ConsentPolicy",
    "PrivacyConsent",
    "NotificationPreference",
    "LicenseCredential",
    "LicenseReview",
    "SpecialtyExpertise",
    "PatientGuardianLink",
    "CareEpisode",
    "Diagnosis",
    "CaseStatusHistory",
    "CareAssignment",
    "DoctorChangeRequest",
    "ClinicalComplaint",
    "TriageResult",
    "UnassignedCase",
    "CaseAssignment",
    "DoctorCandidateReview",
    "MedicalRecord",
    "DemographicProfile",
    "MedicalHistoryEntry",
    "ChronicCondition",
    "ClinicalDocument",
    "ImagingStudy",
    "ImagingSeries",
    "ImagingInstance",
    "ImagingQualityCheck",
    "ClinicalInterpretation",
    "SimplifiedExplanation",
    "RecordShareRequest",
    "ShareRecipient",
    "RecordShareItem",
    "ReferralSummary",
    "CommunityShareConsent",
    "AnonymizedCaseSnapshot",
    "Exercise",
    "ExerciseMedia",
    "ExerciseCategory",
    "ExerciseCategoryLink",
    "SafeAngularRange",
    "Contraindication",
    "ClinicalProtocol",
    "RehabilitationPlan",
    "PlanExercise",
    "PlanRevision",
    "ProviderAvailability",
    "AppointmentSlot",
    "Appointment",
    "AppointmentStatusHistory",
    "RehabSession",
    "SessionAssessment",
    "SessionAttendance",
    "SessionReminder",
    "CaregiverGuidance",
    "AIEngine",
    "DeviceCaptureSession",
    "MotionAnalysis",
    "MotionSample",
    "JointMeasurement",
    "MotionFeedbackEvent",
    "VitalSignObservation",
    "SafetyIncident",
    "EmergencyStop",
    "MotionReview",
    "GamificationProfile",
    "RewardPointTx",
    "RewardCatalog",
    "RewardRedemption",
    "Badge",
    "PatientBadge",
    "MotivationMessage",
    "DailyRecoveryBoard",
    "ClinicalRule",
    "ClinicalRuleCondition",
    "ClinicalRuleAction",
    "RuleExecutionLog",
    "MedicalReference",
    "ClinicalRuleProposal",
    "AIServiceSetting",
    "AIModelVersion",
    "AIPerformanceMetric",
    "AIRun",
    "AIRunIO",
    "AIApproval",
    "ImagingAIAnalysis",
    "RelapseRiskAnalysis",
    "RAGDocument",
    "RAGChunk",
    "EmbeddingIndex",
    "TrustedQAAnswer",
    "NotificationTemplate",
    "Notification",
    "NotificationDelivery",
    "UserNotificationState",
    "MotorDeclineAlert",
    "TherapeuticWarning",
    "ClinicalEarlyWarning",
    "IncidentDocumentation",
    "FollowUpNotification",
    "Conversation",
    "ConversationParticipant",
    "Message",
    "MessageAttachment",
    "MessageDelivery",
    "MessageReadReceipt",
    "UrgentContactRequest",
    "EmergencyHelpRequest",
    "ClinicalConsultation",
    "ConsultationResponse",
    "ConsultationReport",
    "SupervisionCase",
    "SupervisionAction",
    "ConsultationAppointment",
    "SmartReport",
    "ReportExport",
    "ProgressReport",
    "DetailedClinicalReport",
    "WeeklyCareSummary",
    "ReportSession",
    "StatisticSnapshot",
    "BackupSchedule",
    "BackupJob",
    "BackupIntegrityCheck",
    "RestoreOperation",
    "RestoreVerification",
    "AuditLogEntry",
    "AuditReviewNote",
    "DataAccessLog",
    "StoredFile",
]
