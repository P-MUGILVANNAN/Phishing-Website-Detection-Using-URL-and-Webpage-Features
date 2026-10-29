import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.models import init_db

init_db()
client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert "version" in data

def test_model_info_endpoint():
    resp = client.get("/api/model/info")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data

def test_predict_url_endpoint():
    resp = client.post("/api/predict/url", json={"url": "https://en.wikipedia.org/wiki/Computer_security"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_success"] is True
    assert "prediction" in data
    assert "model_score" in data
    assert "explanation" in data

def test_predict_batch_endpoint():
    resp = client.post(
        "/api/predict/batch",
        json={"urls": ["https://python.org", "https://github.com"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_processed"] == 2

def test_dashboard_summary_endpoint():
    resp = client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_analyzed" in data

def test_predictions_history_endpoint():
    resp = client.get("/api/predictions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_model_evaluation_endpoint():
    resp = client.get("/api/model/evaluation")
    assert resp.status_code == 200
    data = resp.json()
    assert "main_model" in data
    assert "baselines" in data
    assert "generalization_comparison" in data

def test_feature_importance_endpoint():
    resp = client.get("/api/model/feature-importance")
    assert resp.status_code == 200
    data = resp.json()
    assert "feature_importance" in data
    assert "shap_importance" in data

def test_dataset_validate_endpoint():
    sample_csv = "url,label\nhttps://google.com,0\nhttp://evil-paypal.com/login,1\n"
    resp = client.post(
        "/api/datasets/validate",
        json={
            "csv_text": sample_csv,
            "url_column": "url",
            "label_column": "label"
        }
    )
    # Less than 10 records returns 422 with meaningful message
    assert resp.status_code == 422
