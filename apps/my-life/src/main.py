import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth as auth_router
from .routers import todos as todos_router
from .routers import budget as budget_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Life",
    description="개인용 할일 관리 + 가계부",
    version="1.0.0",
    docs_url=None,   # Swagger는 /docs 에서 수동 노출 (아래 참고)
    redoc_url=None,
)

app.include_router(auth_router.router)
app.include_router(todos_router.router)
app.include_router(budget_router.router)

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


# Swagger: 인증된 사용자만 접근
from fastapi.openapi.docs import get_swagger_ui_html
from .auth import verify_session


@app.get("/docs", include_in_schema=False)
def swagger_ui(request: Request):
    if not verify_session(request):
        return HTMLResponse("<h3>401 Unauthorized — 먼저 로그인하세요</h3>", status_code=401)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="My Life API")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)
