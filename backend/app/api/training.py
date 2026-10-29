from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends
import pandas as pd
from app.schemas.dataset import ModelTrainRequest
from app.services.training_service import training_service
from app.services.dataset_service import dataset_service
from app.database.repository import repo
from app.core.security import verify_admin_access
from app.config import settings

router = APIRouter()

@router.post("/model/train", dependencies=[Depends(verify_admin_access)])
def trigger_training(req: ModelTrainRequest):
    if training_service.is_training:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A model training job is currently in progress."
        )

    # If csv_text is provided, validate and parse it
    if req.csv_text:
        val_res = dataset_service.validate_and_parse_csv(
            csv_content=req.csv_text,
            url_col=req.url_column,
            label_col=req.label_column,
            html_col=req.html_column
        )
        if not val_res["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid dataset: {val_res['error_message']}"
            )
        clean_df = val_res["clean_df"]
    else:
        # Load from default processed research dataset in data/
        default_data_path = settings.BASE_DIR.parent / "data" / "processed" / "phishguard_research_dataset.csv"
        if not default_data_path.exists():
            default_data_path = settings.BASE_DIR.parent / "data" / "sample" / "synthetic_test_dataset.csv"

        if not default_data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No default research dataset found on disk. Please upload a dataset to train."
            )
        clean_df = pd.read_csv(default_data_path)

    xgb_params = {
        "n_estimators": req.n_estimators,
        "max_depth": req.max_depth,
        "learning_rate": req.learning_rate
    }

    try:
        train_res = training_service.run_training_task(
            df=clean_df,
            url_col="url",
            label_col="label",
            html_col="html_text" if "html_text" in clean_df.columns else None,
            test_size=req.test_size,
            xgb_params=xgb_params
        )
        return train_res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )

@router.get("/model/training-status")
def get_training_status():
    latest_job = repo.get_latest_training_job()
    return {
        "is_training": training_service.is_training,
        "latest_job": latest_job
    }

