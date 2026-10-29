from typing import Dict, Any, List, Optional
import numpy as np
import shap

from app.ml.predict import model_predictor
from app.ml.pipeline import FEATURE_DESCRIPTIONS, ALL_FEATURE_NAMES
from app.core.logging_config import logger

class ExplanationService:
    def __init__(self):
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        if model_predictor.is_loaded and model_predictor.raw_xgb is not None:
            try:
                self.explainer = shap.TreeExplainer(model_predictor.raw_xgb)
            except Exception as e:
                logger.warning(f"Could not initialize SHAP TreeExplainer: {e}")
                self.explainer = None

    def explain_prediction(
        self,
        prediction_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        if self.explainer is None and model_predictor.is_loaded:
            self._init_explainer()

        feature_vector = np.array([prediction_result["feature_vector"]], dtype=np.float32)
        feature_dict = prediction_result["features"]
        feature_names = ALL_FEATURE_NAMES

        contributions: List[Dict[str, Any]] = []

        if self.explainer is not None:
            try:
                shap_vals = self.explainer.shap_values(feature_vector)[0]
                for fname, val, s_val in zip(feature_names, feature_vector[0], shap_vals):
                    contributions.append({
                        "feature_name": fname,
                        "description": FEATURE_DESCRIPTIONS.get(fname, fname),
                        "observed_value": float(val),
                        "shap_value": round(float(s_val), 4),
                        "impact": "phishing" if s_val > 0 else "legitimate",
                        "magnitude": abs(float(s_val))
                    })
            except Exception as e:
                logger.warning(f"Error computing individual SHAP values: {e}")

        # Fallback to heuristic feature contributions if SHAP is unavailable
        if not contributions:
            for fname in feature_names:
                val = float(feature_dict.get(fname, 0.0))
                # Heuristic risk assignment
                if fname in ("has_ip_hostname", "has_brand_in_subdomain", "title_domain_mismatch", "has_external_form_action") and val > 0:
                    s_val = 0.5 * val
                elif fname in ("is_https",) and val > 0:
                    s_val = -0.1
                elif fname in ("suspicious_words_count", "urgency_keyword_freq", "login_keyword_freq") and val > 0:
                    s_val = 0.15 * min(val, 3)
                else:
                    s_val = 0.0
                    
                contributions.append({
                    "feature_name": fname,
                    "description": FEATURE_DESCRIPTIONS.get(fname, fname),
                    "observed_value": float(val),
                    "shap_value": round(float(s_val), 4),
                    "impact": "phishing" if s_val > 0 else "legitimate",
                    "magnitude": abs(float(s_val))
                })

        # Sort by impact magnitude
        contributions.sort(key=lambda x: x["magnitude"], reverse=True)

        # Top phishing drivers
        phishing_drivers = [c for c in contributions if c["impact"] == "phishing" and c["magnitude"] > 0.01][:5]
        # Top legitimate drivers
        legitimate_drivers = [c for c in contributions if c["impact"] == "legitimate" and c["magnitude"] > 0.01][:5]

        # Natural language insights
        insights = []
        if feature_dict.get("has_ip_hostname", 0) == 1:
            insights.append("URL uses a raw IP address instead of a recognized domain name.")
        if feature_dict.get("has_brand_in_subdomain", 0) == 1:
            insights.append("A prominent brand name is present in a subdomain, a common credential phishing tactic.")
        if feature_dict.get("title_domain_mismatch", 0) == 1:
            insights.append("The page title claims to represent a brand not matching the registered domain.")
        if feature_dict.get("has_external_form_action", 0) == 1:
            insights.append("Webpage form submits sensitive form data to a foreign registered domain.")
        if feature_dict.get("has_login_form", 0) == 1 and feature_dict.get("urgency_keyword_freq", 0) > 0:
            insights.append("Detected login form alongside artificial urgency or account-suspension language.")
        if feature_dict.get("is_https", 0) == 1:
            insights.append("HTTPS protocol is enabled (Note: HTTPS provides encryption, not proof of legitimacy).")
        if feature_dict.get("digit_ratio", 0) > 0.25:
            insights.append(f"High concentration of numeric characters ({int(feature_dict['digit_ratio']*100)}% of URL).")

        if not insights:
            if prediction_result["prediction"] == "Legitimate":
                insights.append("Lexical metrics and domain characteristics align with standard legitimate patterns.")
            else:
                insights.append("Multiple subtle structural and lexical indicators contributed to the elevated risk score.")

        # Missing features notification
        missing_features = []
        if feature_dict.get("page_features_available", 0) == 0:
            missing_features.append("Webpage HTML structure and text NLP features were not retrieved (analyzed via URL features only).")

        return {
            "prediction": prediction_result["prediction"],
            "model_score": prediction_result["model_score"],
            "risk_label": prediction_result["risk_label"],
            "top_phishing_factors": phishing_drivers,
            "top_legitimate_factors": legitimate_drivers,
            "plain_text_insights": insights,
            "missing_features": missing_features,
            "disclaimer": "Automated security prediction. Machine learning indicators do not constitute guarantee of safety or malicious intent."
        }

explanation_service = ExplanationService()
