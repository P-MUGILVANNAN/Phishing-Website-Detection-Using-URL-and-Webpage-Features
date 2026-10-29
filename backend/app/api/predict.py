from fastapi import APIRouter, HTTPException, status
from app.schemas.prediction import URLPredictionRequest, BatchPredictionRequest
from app.services.prediction_service import prediction_service

router = APIRouter()

@router.post("/predict/url")
def predict_url(req: URLPredictionRequest):
    res = prediction_service.analyze_single_url(
        url=req.url,
        enable_fetch=req.enable_fetch
    )
    if not res.get("is_success"):
        if res.get("model_status") == "UNTRAINED":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model is currently untrained. Upload a dataset or train the model to enable inference."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("error", "Failed to analyze URL.")
        )
    return res

@router.post("/predict/batch")
def predict_batch(req: BatchPredictionRequest):
    if len(req.urls) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch exceeds maximum allowed limit of 500 URLs."
        )
    return prediction_service.analyze_batch(
        urls=req.urls,
        enable_fetch=req.enable_fetch
    )

