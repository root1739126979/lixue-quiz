from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers import admin, auth, banks, exams, practice, rankings, wrong_questions
from app.security import decode_access_token


def create_app() -> FastAPI:
    Base.metadata.create_all(engine)
    app = FastAPI(title="砺学刷题平台 API")
    app.include_router(auth.router)
    app.include_router(banks.router)
    app.include_router(admin.router)
    app.include_router(practice.router)
    app.include_router(wrong_questions.router)
    app.include_router(rankings.router)
    app.include_router(exams.router)

    @app.middleware("http")
    async def require_admin_token(request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/admin") and path != "/api/admin/auth/login":
            authorization = request.headers.get("authorization", "")
            if not authorization.lower().startswith("bearer "):
                return JSONResponse(
                    {"detail": "未登录"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                payload = decode_access_token(authorization.split(" ", 1)[1])
            except Exception:
                return JSONResponse(
                    {"detail": "无效 token"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            if payload.get("role") != "admin":
                return JSONResponse(
                    {"detail": "权限不足"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return await call_next(request)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
