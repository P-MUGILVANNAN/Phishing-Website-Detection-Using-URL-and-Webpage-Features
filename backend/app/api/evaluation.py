from fastapi import APIRouter, HTTPException, status
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.get("/model/info")
def get_model_info():
    return evaluation_service.get_model_info()

@router.get("/model/evaluation")
def get_evaluation():
    data = evaluation_service.get_evaluation_metrics()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evaluation metrics found. Please train the model to compute evaluation benchmarks."
        )
    return data

@router.get("/model/feature-importance")
def get_feature_importance():
    data = evaluation_service.get_feature_importance()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feature importance data found. Train the model to generate feature contributions."
        )
    return data

