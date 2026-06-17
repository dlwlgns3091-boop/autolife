from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./work_planner.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Add new columns to existing tables using ALTER TABLE (data-safe)."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        existing = {row[1] for row in result}
        if "task_source" not in existing:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN task_source VARCHAR(10)"))
            conn.execute(text("UPDATE tasks SET task_source = '직접' WHERE task_source IS NULL"))
            conn.commit()
