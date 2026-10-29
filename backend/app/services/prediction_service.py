import time
from typing import Dict, Any, Optional, List
from app.services.url_normalizer import URLNormalizer
from app.services.url_fetcher import safe_fetcher, FetchResult
from app.services.domain_parser import domain_parser
from app.ml.predict import model_predictor
from app.services.explanation_service import explanation_service
from app.database.repository import repo
from app.config import settings

class PredictionService:
    @staticmethod
    def analyze_single_url(
        url: str,
        enable_fetch: bool = False
    ) -> Dict[str, Any]:
        norm = URLNormalizer.normalize(url)
        if not norm.is_valid:
            return {
                "is_success": False,
                "error": norm.error_message or "Invalid URL provided.",
                "url": url,
                "normalized_url": None,
                "registered_domain": None,
                "prediction": None,
                "model_score": None,
                "explanation": None
            }

        parsed_dom = domain_parser.parse(norm.hostname)
        reg_domain = parsed_dom.registered_domain

        # Optional safe webpage fetch
        html_content = None
        fetch_status = "SKIPPED_NOT_REQUESTED"
        fetch_error = None
        fetch_status_code = None

        if enable_fetch:
            fetch_res: FetchResult = safe_fetcher.fetch(norm.normalized_url)
            fetch_status_code = fetch_res.status_code
            if fetch_res.is_success:
                html_content = fetch_res.html_content
                fetch_status = "SUCCESS"
            else:
                fetch_status = "BLOCKED_OR_FAILED"
                fetch_error = fetch_res.error_message

        # Perform ML Prediction
        try:
            pred_res = model_predictor.predict_single(
                url=norm.normalized_url,
                html_content=html_content
            )
        except RuntimeError as e:
            return {
                "is_success": False,
                "error": str(e),
                "url": url,
                "normalized_url": norm.normalized_url,
                "registered_domain": reg_domain,
                "model_status": "UNTRAINED"
            }

        # Generate Explainable AI Report
        explanation = explanation_service.explain_prediction(pred_res)

        # Analysis mode
        analysis_mode = "URL + Safe Webpage Fetch" if (enable_fetch and html_content) else "URL Only"

        # Persist to SQLite
        pred_id = repo.add_prediction(
            submitted_url=norm.original_url,
            normalized_domain=reg_domain,
            prediction=pred_res["prediction"],
            model_score=pred_res["model_score"],
            analysis_mode=analysis_mode,
            fetch_status=fetch_status,
            model_version=pred_res["model_version"],
            feature_schema_version=settings.FEATURE_SCHEMA_VERSION,
            explanation_dict=explanation
        )

        return {
            "is_success": True,
            "prediction_id": pred_id,
            "url": norm.original_url,
            "normalized_url": norm.normalized_url,
            "registered_domain": reg_domain,
            "prediction": pred_res["prediction"],
            "model_score": pred_res["model_score"],
            "risk_label": pred_res["risk_label"],
            "risk_level": pred_res["risk_level"],
            "calibrated_probability": pred_res["calibrated_probability"],
            "thresholds": pred_res["thresholds"],
            "analysis_mode": analysis_mode,
            "webpage_fetch": {
                "status": fetch_status,
                "status_code": fetch_status_code,
                "error": fetch_error
            },
            "explanation": explanation,
            "features_summary": {
                "url_length": pred_res["features"]["url_length"],
                "has_ip_hostname": pred_res["features"]["has_ip_hostname"],
                "is_https": pred_res["features"]["is_https"],
                "subdomain_depth": pred_res["features"]["subdomain_depth"],
                "has_brand_in_subdomain": pred_res["features"]["has_brand_in_subdomain"],
                "has_login_form": pred_res["features"].get("has_login_form", 0),
                "title_domain_mismatch": pred_res["features"].get("title_domain_mismatch", 0)
            },
            "model_version": pred_res["model_version"]
        }

    @classmethod
    def analyze_batch(
        cls,
        urls: List[str],
        enable_fetch: bool = False
    ) -> Dict[str, Any]:
        results = []
        counts = {"Legitimate": 0, "Phishing": 0, "Suspicious / Uncertain": 0, "Error": 0}

        for u in urls[:500]: # Batch safeguard limit
            if not u.strip():
                continue
            res = cls.analyze_single_url(u.strip(), enable_fetch=enable_fetch)
            if res.get("is_success"):
                pred = res["prediction"]
                counts[pred] = counts.get(pred, 0) + 1
            else:
                counts["Error"] += 1
            results.append(res)

        return {
            "total_processed": len(results),
            "summary_counts": counts,
            "items": results
        }

prediction_service = PredictionService()

