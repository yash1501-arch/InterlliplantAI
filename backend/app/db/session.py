from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import settings
from app.db.models import Base

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "intelliplant.db"

DATABASE_URL = settings.database_url
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL.replace("sqlite:///./", f"sqlite:///{DB_DIR.as_posix()}/"), echo=settings.debug)
else:
    engine = create_engine(DATABASE_URL, echo=settings.debug)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def init_models():
    Base.metadata.create_all(bind=engine)
