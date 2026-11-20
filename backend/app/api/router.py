from fastapi import APIRouter

from app.api.v1 import admin, auth, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)


# يُرجع حالة الخادم للتأكد من أنه يعمل.
@api_router.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok", "service": "faith-in-life"}
