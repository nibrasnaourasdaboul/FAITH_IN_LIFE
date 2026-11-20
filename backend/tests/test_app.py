import asyncio
from urllib.parse import urlsplit

import asyncpg

from tests.conftest import TEST_DATABASE_URL


# يتأكد أن الخادم يرد وأن قاعدة الاختبار هي PostgreSQL وفيها دور الوصي.
def test_health_uses_postgresql(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "faith-in-life"}

    parts = urlsplit(TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql", 1))

    async def read_database():
        connection = await asyncpg.connect(
            user=parts.username,
            password=parts.password,
            host=parts.hostname,
            port=parts.port,
            database=parts.path.lstrip("/"),
        )
        try:
            name = await connection.fetchval("SELECT current_database()")
            version = await connection.fetchval("SELECT version()")
            role = await connection.fetchval("SELECT role_name FROM roles WHERE role_code = 'guardian'")
            return name, version, role
        finally:
            await connection.close()

    name, version, role = asyncio.run(read_database())
    assert name == "faith_in_life_test"
    assert "PostgreSQL" in version
    assert role == "Guardian"


# يسجّل دخول المدير من البيانات المزروعة في PostgreSQL.
def test_admin_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@faithinlife.local", "password": "ChangeMe!2026"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["home"] == "/app/admin"
    assert "admin" in body["user"]["roles"]


# يرفض كلمة مرور خاطئة دون فتح جلسة.
def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@faithinlife.local", "password": "not-the-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_credentials"
