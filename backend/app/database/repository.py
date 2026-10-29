import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.database.models import get_db_connection

class DatabaseRepository:
    @staticmethod
    def add_prediction(
        submitted_url: str,
        normalized_domain: str,
        prediction: str,
        model_score: float,
        analysis_mode: str,
        fetch_status: str,
        model_version: str,
        feature_schema_version: str,
        explanation_dict: Optional[Dict[str, Any]] = None
    ) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        explanation_json = json.dumps(explanation_dict, default=lambda o: float(o) if hasattr(o, "item") else str(o)) if explanation_dict else "{}"
        
        cursor.execute(
            """
            INSERT INTO PredictionHistory 
            (submitted_url, normalized_domain, prediction, model_score, analysis_mode, fetch_status, model_version, feature_schema_version, explanation_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submitted_url,
                normalized_domain,
                prediction,
                model_score,
                analysis_mode,
                fetch_status,
                model_version,
                feature_schema_version,
                explanation_json,
                created_at
            )
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    @staticmethod
    def get_predictions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, submitted_url, normalized_domain, prediction, model_score, analysis_mode, fetch_status, model_version, feature_schema_version, created_at
            FROM PredictionHistory
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_prediction_by_id(prediction_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM PredictionHistory WHERE id = ?",
            (prediction_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        if res.get("explanation_json"):
            try:
                res["explanation"] = json.loads(res["explanation_json"])
            except Exception:
                res["explanation"] = {}
        return res

    @staticmethod
    def get_dashboard_summary() -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM PredictionHistory")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as phish FROM PredictionHistory WHERE prediction = 'Phishing'")
        phish = cursor.fetchone()["phish"]

        cursor.execute("SELECT COUNT(*) as legit FROM PredictionHistory WHERE prediction = 'Legitimate'")
        legit = cursor.fetchone()["legit"]

        cursor.execute("SELECT COUNT(*) as uncertain FROM PredictionHistory WHERE prediction LIKE '%Suspicious%' OR prediction LIKE '%Uncertain%'")
        uncertain = cursor.fetchone()["uncertain"]

        cursor.execute(
            """
            SELECT id, submitted_url, normalized_domain, prediction, model_score, analysis_mode, created_at 
            FROM PredictionHistory 
            ORDER BY id DESC LIMIT 5
            """
        )
        recent = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return {
            "total_analyzed": total,
            "phishing_count": phish,
            "legitimate_count": legit,
            "uncertain_count": uncertain,
            "recent_predictions": recent
        }

    @staticmethod
    def create_training_job() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO TrainingJob (status, progress, started_at) VALUES (?, ?, ?)",
            ("RUNNING", 10, now)
        )
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return job_id

    @staticmethod
    def update_training_job(job_id: int, status: str, progress: int, error_summary: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        finished_at = datetime.now().isoformat() if status in ("COMPLETED", "FAILED") else None
        cursor.execute(
            "UPDATE TrainingJob SET status = ?, progress = ?, finished_at = ?, error_summary = ? WHERE id = ?",
            (status, progress, finished_at, error_summary, job_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_latest_training_job() -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TrainingJob ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def log_audit(actor: str, action: str, resource: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO AuditLog (actor, action, resource, created_at) VALUES (?, ?, ?, ?)",
            (actor, action, resource, now)
        )
        conn.commit()
        conn.close()

repo = DatabaseRepository()
