from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

from .database import engine
from .models import Base
from .routers import categories, tasks, templates

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Work Planner API",
    description="업무 계획 관리 앱 API",
    version="1.0.0",
)

app.include_router(categories.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(templates.router, prefix="/api")

_static = pathlib.Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(_static)), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(str(_static / "index.html"))
