from fastapi import APIRouter
from app.config import settings
from app.ml.predict import model_predictor
from app.database.models import get_db_connection

router = APIRouter()

@router.get("/health")
def get_health():
    db_ok = False
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_connected": db_ok,
        "model_loaded": model_predictor.is_loaded,
        "model_version": model_predictor.metadata.get("model_version") if model_predictor.is_loaded else None,
        "webpage_fetch_enabled": settings.ENABLE_WEBPAGE_FETCH
    }

