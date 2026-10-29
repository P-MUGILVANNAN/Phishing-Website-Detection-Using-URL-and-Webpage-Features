from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DatasetValidateRequest(BaseModel):
    csv_text: str = Field(..., description="Raw CSV string content")
    url_column: str = Field("url", description="Name of the URL column")
    label_column: str = Field("label", description="Name of the label column")
    html_column: Optional[str] = Field("html_text", description="Name of optional HTML column")
    custom_label_map: Optional[Dict[str, int]] = Field(None, description="Custom label value mapping")

class ModelTrainRequest(BaseModel):
    csv_text: Optional[str] = Field(None, description="CSV content. If null, trains on the existing verified research dataset.")
    url_column: str = "url"
    label_column: str = "label"
    html_column: Optional[str] = "html_text"
    test_size: float = Field(0.20, ge=0.1, le=0.4)
    n_estimators: int = Field(150, ge=50, le=500)
    max_depth: int = Field(5, ge=2, le=12)
    learning_rate: float = Field(0.08, ge=0.01, le=0.5)

