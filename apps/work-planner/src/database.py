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
    """Apply incremental schema changes without dropping existing data."""
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN source VARCHAR(10) DEFAULT '직접'"))
            conn.execute(text("UPDATE tasks SET source = '직접' WHERE source IS NULL"))
            conn.commit()
        except Exception:
            # Column already exists — safe to ignore
            pass
