from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base, SessionLocal
from .routers import step0, weekly, monthly, immediate, dashboard
from .seed import run_seed

Base.metadata.create_all(bind=engine)

app = FastAPI(title="마케팅 데스크", description="마케팅 데스크 업무 관리 앱", version="1.0.0")

app.include_router(step0.router)
app.include_router(weekly.router)
app.include_router(monthly.router)
app.include_router(immediate.router)
app.include_router(dashboard.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
