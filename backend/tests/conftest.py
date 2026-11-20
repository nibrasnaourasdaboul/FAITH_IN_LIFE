import asyncio
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import asyncpg
import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent


# يقرأ عنوان PostgreSQL من ملف البيئة ويستبدل اسم القاعدة بقاعدة الاختبار.
def _postgres_test_url() -> str:
    url = ""
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            url = line.split("=", 1)[1].strip()
            break
    if not url.startswith("postgresql"):
        raise RuntimeError("DATABASE_URL must point at PostgreSQL.")
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, "/faith_in_life_test", "", ""))


TEST_DATABASE_URL = _postgres_test_url()
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


# ينشئ قاعدة الاختبار على خادم PostgreSQL إذا لم تكن موجودة.
def _ensure_test_database() -> None:
    parts = urlsplit(TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql", 1))
    name = parts.path.lstrip("/")

    async def create() -> None:
        connection = await asyncpg.connect(
            user=parts.username,
            password=parts.password,
            host=parts.hostname,
            port=parts.port,
            database="postgres",
        )
        try:
            exists = await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", name)
            if not exists:
                await connection.execute(f'CREATE DATABASE "{name}"')
        finally:
            await connection.close()

    asyncio.run(create())


_ensure_test_database()
subprocess.run(
    [sys.executable, "-m", "alembic", "upgrade", "head"],
    cwd=BACKEND,
    env={**os.environ, "DATABASE_URL": TEST_DATABASE_URL},
    check=True,
)

from app.main import create_app  # noqa: E402


# يشغّل التطبيق على قاعدة الاختبار طوال جلسة الاختبار.
@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client
