import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings
from app.ml.predict import model_predictor

class EvaluationService:
    @staticmethod
    def get_evaluation_metrics() -> Optional[Dict[str, Any]]:
        eval_path = settings.ARTIFACTS_DIR / "evaluation.json"
        if not eval_path.exists():
            return None
        with open(eval_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_feature_importance() -> Optional[Dict[str, Any]]:
        eval_path = settings.ARTIFACTS_DIR / "evaluation.json"
        schema_path = settings.ARTIFACTS_DIR / "feature_schema.json"
        if not eval_path.exists():
            return None

        with open(eval_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        descriptions = {}
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                descriptions = json.load(f).get("descriptions", {})

        return {
            "model_version": eval_data.get("model_version"),
            "feature_importance": eval_data.get("feature_importance", {}),
            "shap_importance": eval_data.get("shap_importance", {}),
            "descriptions": descriptions
        }

    @staticmethod
    def get_model_info() -> Dict[str, Any]:
        meta_path = settings.ARTIFACTS_DIR / "metadata.json"
        if not meta_path.exists() or not model_predictor.is_loaded:
            return {
                "status": "UNTRAINED",
                "message": "No trained model currently available in artifacts.",
                "feature_schema_version": settings.FEATURE_SCHEMA_VERSION,
                "thresholds": {
                    "legitimate": settings.THRESHOLD_LEGITIMATE,
                    "phishing": settings.THRESHOLD_PHISHING
                }
            }

        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return {
            "status": "TRAINED",
            "metadata": metadata
        }

evaluation_service = EvaluationService()

