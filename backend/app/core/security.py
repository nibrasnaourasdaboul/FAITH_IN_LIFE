import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# يحفظ كلمة المرور بصيغة لا يمكن عكسها.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# يقارن كلمة المرور المدخلة بالقيمة المحفوظة.
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password, password_hash)
    except ValueError:
        return False


# يصنع بصمة للرمز حتى لا يُحفظ الرمز نفسه.
def hash_token(raw: str) -> str:
    pepper = get_settings().secret_key
    return hashlib.sha256(f"{raw}:{pepper}".encode()).hexdigest()


# ينشئ رمز تحقق من ستة أرقام.
def new_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


# يتأكد أن الرمز المدخل يطابق البصمة المحفوظة.
def otp_matches(raw: str, digest: str) -> bool:
    return hmac.compare_digest(hash_token(raw), digest)


# يصدر رمز دخول قصير العمر يحمل هوية المستخدم وأدواره.
def create_access_token(user_id: uuid.UUID, roles: list[str]) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


# يصدر رمز تحديث أطول عمراً مرتبطاً بالجلسة.
def create_refresh_token(user_id: uuid.UUID, session_id: uuid.UUID) -> tuple[str, str, datetime]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=settings.refresh_token_days)
    jti = secrets.token_urlsafe(32)
    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, jti, expires


# يقرأ الرمز الموقّع ويتحقق من صحته.
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise ValueError("invalid_token") from exc
