from fastapi import APIRouter, HTTPException, status, Query
from app.database.repository import repo
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.get("/predictions")
def list_predictions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    return repo.get_predictions(limit=limit, offset=offset)

@router.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int):
    record = repo.get_prediction_by_id(prediction_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction record #{prediction_id} not found."
        )
    return record

@router.get("/dashboard/summary")
def get_dashboard_summary():
    summary = repo.get_dashboard_summary()
    model_info = evaluation_service.get_model_info()
    eval_metrics = evaluation_service.get_evaluation_metrics()
    
    return {
        **summary,
        "model_status": model_info.get("status", "UNTRAINED"),
        "model_version": model_info.get("metadata", {}).get("model_version") if model_info.get("status") == "TRAINED" else None,
        "evaluation_summary": eval_metrics.get("main_model", {}).get("metrics") if eval_metrics else None,
        "generalization_gap": eval_metrics.get("generalization_comparison") if eval_metrics else None
    }

@router.get("/reports/{prediction_id}")
def get_prediction_report(prediction_id: int):
    record = repo.get_prediction_by_id(prediction_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction record #{prediction_id} not found."
        )

    explanation = record.get("explanation", {})

    report_data = {
        "report_id": f"REP-PHISH-{record['id']:06d}",
        "analysis_date": record["created_at"],
        "analyzed_target": {
            "submitted_url": record["submitted_url"],
            "registered_domain": record["normalized_domain"],
            "analysis_mode": record["analysis_mode"],
            "fetch_status": record["fetch_status"]
        },
        "model_assessment": {
            "prediction": record["prediction"],
            "risk_score": record["model_score"],
            "risk_label": explanation.get("risk_label", record["prediction"]),
            "model_version": record["model_version"],
            "schema_version": record["feature_schema_version"]
        },
        "explainable_evidence": {
            "top_phishing_factors": explanation.get("top_phishing_factors", []),
            "top_legitimate_factors": explanation.get("top_legitimate_factors", []),
            "plain_text_insights": explanation.get("plain_text_insights", []),
            "missing_features": explanation.get("missing_features", [])
        },
        "disclaimer": explanation.get("disclaimer", "Automated security prediction. Machine learning indicators do not constitute guarantee of safety or malicious intent.")
    }
    return report_data

