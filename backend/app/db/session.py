import logging
import socket
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def is_postgres_available(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if PostgreSQL server port is open and reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def create_db_engine():
    db_url = settings.get_database_url()
    
    if "postgresql" in db_url:
        host = settings.POSTGRES_HOST
        port = settings.POSTGRES_PORT
        # If postgres server is reachable, connect with pool configuration
        if is_postgres_available(host, port):
            logger.info(f"Connecting to PostgreSQL database at {host}:{port}/{settings.POSTGRES_DB}")
            return create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=False
            )
        else:
            logger.warning(
                f"PostgreSQL server not detected at {host}:{port}. "
                f"Automatically using local SQLite fallback (smart_irrigation.db) for development."
            )
            return create_engine(
                "sqlite:///./smart_irrigation.db",
                connect_args={"check_same_thread": False},
                echo=False
            )
    else:
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
