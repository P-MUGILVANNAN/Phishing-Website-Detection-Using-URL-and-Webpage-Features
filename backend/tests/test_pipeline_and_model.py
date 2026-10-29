import pytest
from app.services.prediction_service import prediction_service
from app.ml.predict import model_predictor
from app.ml.pipeline import pipeline, ALL_FEATURE_NAMES

def test_pipeline_feature_names_length():
    assert len(ALL_FEATURE_NAMES) == 52

def test_pipeline_extraction_single():
    res = pipeline.extract_features_single("https://google.com")
    assert len(res["feature_vector"]) == 52
    assert res["feature_dict"]["is_https"] == 1
    assert res["feature_dict"]["has_ip_hostname"] == 0

def test_prediction_service_single_legitimate():
    res = prediction_service.analyze_single_url("https://www.google.com/search")
    assert res["is_success"] is True
    assert res["prediction"] in ("Legitimate", "Suspicious / Uncertain", "Phishing")
    assert res["model_score"] >= 0.0 and res["model_score"] <= 1.0
    assert "explanation" in res
    assert len(res["explanation"]["top_legitimate_factors"]) >= 0

def test_prediction_service_single_phishing():
    res = prediction_service.analyze_single_url("http://paypal-security-verification-portal.com/login.php")
    assert res["is_success"] is True
    assert res["prediction"] in ("Legitimate", "Suspicious / Uncertain", "Phishing")
    assert res["explanation"] is not None
    assert len(res["explanation"]["top_phishing_factors"]) > 0

def test_prediction_service_batch():
    urls = [
        "https://en.wikipedia.org/wiki/Phishing",
        "http://netflix-billing-update-required.net/signin"
    ]
    batch_res = prediction_service.analyze_batch(urls)
    assert batch_res["total_processed"] == 2
    assert len(batch_res["items"]) == 2
