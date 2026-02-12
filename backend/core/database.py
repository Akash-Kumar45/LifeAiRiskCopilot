from typing import Generator
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./lifeai_risk_copilot.db"

# For local dev sqlite; check_same_thread is required for SQLite + multiple threads
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    """Create database tables from SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel Session. Use as a FastAPI dependency."""
    with Session(engine) as session:
        yield session
