import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.errors import AppError
from app.core.redis import close_redis
from app.db.seed import seed
from app.services.storage import storage

logger = logging.getLogger(__name__)


# يشغّل تهيئة قاعدة البيانات والتخزين عند إقلاع الخادم، ثم يغلق الاتصال عند الإيقاف.
@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.basicConfig(level=logging.INFO)
    storage.ensure_layout()
    settings = get_settings()
    if settings.seed_on_startup:
        async with SessionLocal() as session:
            await seed(session)
        logger.info("Reference data is ready.")
    yield
    await close_redis()


# ينشئ تطبيق  FastAPI مع المسارات والوسائط ومعالج الأخطاء.
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # يحوّل أخطاء التطبيق إلى استجابة واضحة تحمل الرمز والرسالة.
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": {"code": exc.code, "message": exc.message}})

    app.include_router(api_router, prefix=settings.api_prefix)
    avatar_dir = Path(settings.storage_root) / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media/avatars", StaticFiles(directory=avatar_dir), name="avatars")
    return app


app = create_app()
