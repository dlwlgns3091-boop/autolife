from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import categories, tasks, templates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Work Planner", description="업무 계획 관리 앱", version="1.0.0")

app.include_router(categories.router)
app.include_router(tasks.router)
app.include_router(templates.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
