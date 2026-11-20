from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FAITH in LIFE"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    secret_key: str = "dev-only-change-me"
    access_token_minutes: int = 20
    refresh_token_days: int = 7
    otp_minutes: int = 10
    database_url: str = "postgresql+asyncpg://postgres:123456@127.0.0.1:3000/faith_in_life"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "FAITH in LIFE <noreply@faithinlife.local>"
    smtp_tls: bool = True
    storage_backend: str = "local"
    storage_root: str = str(BACKEND_ROOT / "storage")
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "faith"
    minio_secret_key: str = "faithsecret"
    minio_secure: bool = False
    public_base_url: str = "http://localhost:8000"
    admin_email: str = "admin@faithinlife.local"
    admin_password: str = "ChangeMe!2026"
    admin_name: str = "System Admin"
    seed_on_startup: bool = True

    # يحوّل عناوين الواجهة المسموحة إلى قائمة.
    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


# يحمّل إعدادات التطبيق من ملف البيئة مرة واحدة.
@lru_cache
def get_settings() -> Settings:
    return Settings()
