from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.core.config import settings

router = APIRouter()

@router.get("/")
def health_check(db: Session = Depends(get_db)):
    """Health check verifying API status and DB connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }
