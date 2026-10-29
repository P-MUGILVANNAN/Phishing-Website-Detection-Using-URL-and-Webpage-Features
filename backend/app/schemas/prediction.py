from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class URLPredictionRequest(BaseModel):
    url: str = Field(..., description="The raw URL to be analyzed")
    enable_fetch: bool = Field(False, description="Whether to perform safe SSRF-guarded webpage HTML inspection")

class BatchPredictionRequest(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to analyze (max 500)")
    enable_fetch: bool = Field(False, description="Whether to perform safe HTML inspection")

class WebpageFetchInfo(BaseModel):
    status: str
    status_code: Optional[int] = None
    error: Optional[str] = None

class FeatureFactor(BaseModel):
    feature_name: str
    description: str
    observed_value: float
    shap_value: float
    impact: str
    magnitude: float

class ExplanationResponse(BaseModel):
    prediction: str
    model_score: float
    risk_label: str
    top_phishing_factors: List[FeatureFactor]
    top_legitimate_factors: List[FeatureFactor]
    plain_text_insights: List[str]
    missing_features: List[str]
    disclaimer: str

class URLPredictionResponse(BaseModel):
    is_success: bool
    prediction_id: Optional[int] = None
    url: str
    normalized_url: Optional[str] = None
    registered_domain: Optional[str] = None
    prediction: Optional[str] = None
    model_score: Optional[float] = None
    risk_label: Optional[str] = None
    risk_level: Optional[str] = None
    calibrated_probability: Optional[float] = None
    thresholds: Optional[Dict[str, float]] = None
    analysis_mode: Optional[str] = None
    webpage_fetch: Optional[WebpageFetchInfo] = None
    explanation: Optional[ExplanationResponse] = None
    features_summary: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    error: Optional[str] = None

