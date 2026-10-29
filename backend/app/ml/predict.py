import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import joblib
import numpy as np

from app.config import settings
from app.ml.pipeline import pipeline, ALL_FEATURE_NAMES
from app.core.logging_config import logger

class ModelPredictor:
    def __init__(self, artifacts_dir: Optional[Path] = None):
        self.artifacts_dir = artifacts_dir or settings.ARTIFACTS_DIR
        self.model = None
        self.raw_xgb = None
        self.metadata = None
        self.feature_schema = None
        self.is_loaded = False
        self.load_model()

    def load_model(self) -> bool:
        model_path = self.artifacts_dir / "model.joblib"
        raw_xgb_path = self.artifacts_dir / "xgb_raw.joblib"
        metadata_path = self.artifacts_dir / "metadata.json"
        schema_path = self.artifacts_dir / "feature_schema.json"

        if not model_path.exists() or not metadata_path.exists():
            logger.info("No trained model artifacts found. System is in untrained state.")
            self.is_loaded = False
            return False

        try:
            self.model = joblib.load(model_path)
            if raw_xgb_path.exists():
                self.raw_xgb = joblib.load(raw_xgb_path)
            else:
                self.raw_xgb = self.model

            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    self.feature_schema = json.load(f)

            self.is_loaded = True
            logger.info(f"Model loaded successfully (Version: {self.metadata.get('model_version')})")
            return True
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            self.is_loaded = False
            return False

    def predict_single(
        self,
        url: str,
        html_content: Optional[str] = None,
        threshold_legitimate: Optional[float] = None,
        threshold_phishing: Optional[float] = None
    ) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model is not trained or loaded. Train the model before running predictions.")

        th_legit = threshold_legitimate if threshold_legitimate is not None else settings.THRESHOLD_LEGITIMATE
        th_phish = threshold_phishing if threshold_phishing is not None else settings.THRESHOLD_PHISHING

        extracted = pipeline.extract_features_single(url=url, html_content=html_content)
        feature_vector = np.array([extracted["feature_vector"]], dtype=np.float32)

        # Predict probability
        try:
            prob = float(self.model.predict_proba(feature_vector)[0, 1])
        except Exception:
            prob = float(self.raw_xgb.predict_proba(feature_vector)[0, 1])

        # Apply 3-class risk categorization policy
        if prob < th_legit:
            decision = "Legitimate"
            risk_label = "Likely legitimate — automated assessment only"
            risk_level = "low"
        elif prob >= th_phish:
            decision = "Phishing"
            risk_label = "Likely phishing — avoid entering credentials until verified"
            risk_level = "high"
        else:
            decision = "Suspicious / Uncertain"
            risk_label = "Suspicious — further verification recommended"
            risk_level = "medium"

        return {
            "prediction": decision,
            "risk_label": risk_label,
            "risk_level": risk_level,
            "model_score": round(prob, 4),
            "calibrated_probability": round(prob, 4) if self.metadata.get("is_calibrated") else None,
            "thresholds": {
                "legitimate": th_legit,
                "phishing": th_phish
            },
            "features": extracted["feature_dict"],
            "feature_vector": extracted["feature_vector"],
            "model_version": self.metadata.get("model_version", "unknown")
        }

model_predictor = ModelPredictor()

