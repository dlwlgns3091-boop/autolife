import os
import tempfile

# Set env vars before any app modules are imported
_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_db.close()
os.environ.setdefault("APP_PASSWORD", "testpass")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db.name}")
