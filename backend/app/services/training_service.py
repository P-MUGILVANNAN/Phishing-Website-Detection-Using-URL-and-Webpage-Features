import threading
from typing import Dict, Any, Optional
import pandas as pd
from app.ml.train import model_trainer
from app.ml.predict import model_predictor
from app.services.explanation_service import explanation_service
from app.database.repository import repo
from app.core.logging_config import logger

class TrainingService:
    def __init__(self):
        self._is_training = False

    @property
    def is_training(self) -> bool:
        return self._is_training

    def run_training_task(
        self,
        df: pd.DataFrame,
        url_col: str = "url",
        label_col: str = "label",
        html_col: Optional[str] = "html_text",
        test_size: float = 0.20,
        xgb_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        job_id = repo.create_training_job()
        self._is_training = True

        try:
            repo.update_training_job(job_id, status="PROCESSING", progress=30)
            res = model_trainer.train(
                df=df,
                url_col=url_col,
                label_col=label_col,
                html_col=html_col,
                test_size=test_size,
                xgb_params=xgb_params
            )
            repo.update_training_job(job_id, status="COMPLETED", progress=100)

            # Reload predictor and explainer in memory
            model_predictor.load_model()
            explanation_service._init_explainer()

            repo.log_audit(
                actor="System/Admin",
                action="TRAIN_MODEL",
                resource=f"Model {res['model_version']}"
            )
            return {"job_id": job_id, "status": "COMPLETED", "result": res}
        except Exception as e:
            logger.error(f"Training job {job_id} failed: {e}")
            repo.update_training_job(job_id, status="FAILED", progress=0, error_summary=str(e))
            raise e
        finally:
            self._is_training = False

training_service = TrainingService()

