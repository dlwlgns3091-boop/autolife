from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base, SessionLocal
from .routers import daily, month_start, month_end, weekly_tasks, always_on, calendar_events, dashboard
from .seed import run_seed

Base.metadata.create_all(bind=engine)

app = FastAPI(title="마케팅 데스크", description="마케팅 업무 관리 앱 v2", version="2.0.0")

app.include_router(daily.router)
app.include_router(month_start.router)
app.include_router(month_end.router)
app.include_router(weekly_tasks.router)
app.include_router(always_on.router)
app.include_router(calendar_events.router)
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
