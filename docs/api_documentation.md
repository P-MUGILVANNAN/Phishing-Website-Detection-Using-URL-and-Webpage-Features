# PhishGuard AI - REST API Documentation

Base URL: `http://localhost:8000/api`

## Endpoints

### 1. Health Status
- **`GET /health`**
- Returns backend operational health, database connectivity, and loaded model version.

### 2. URL Prediction
- **`POST /predict/url`**
- **Request Body**:
  ```json
  {
    "url": "https://secure-login.example.com/auth",
    "enable_fetch": false
  }
  ```
- **Response**:
  ```json
  {
    "is_success": true,
    "prediction_id": 1,
    "url": "https://secure-login.example.com/auth",
    "registered_domain": "example.com",
    "prediction": "Legitimate",
    "model_score": 0.0521,
    "risk_label": "Likely legitimate — automated assessment only",
    "risk_level": "low",
    "explanation": {
      "top_phishing_factors": [],
      "top_legitimate_factors": [],
      "plain_text_insights": ["HTTPS protocol is enabled"],
      "disclaimer": "Automated security prediction."
    }
  }
  ```

### 3. Batch URL Screening
- **`POST /predict/batch`**
- **Request Body**:
  ```json
  {
    "urls": ["https://google.com", "http://paypal-verify.xyz/login"],
    "enable_fetch": false
  }
  ```

### 4. Operational Dashboard Summary
- **`GET /dashboard/summary`**
- Returns aggregate prediction counts, recent scan logs, and real evaluation benchmark summaries.

### 5. Benchmark Evaluation Metrics
- **`GET /model/evaluation`**
- Returns empirical metrics (Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, PR-AUC, Confusion Matrix, Generalization Gap) computed on held-out unseen domains.

### 6. Feature Importance & SHAP
- **`GET /model/feature-importance`**
- Returns XGBoost gain importances, SHAP summary values, and descriptions for all 52 features.

### 7. Dataset Validation
- **`POST /datasets/validate`**
- Accepts CSV text or multipart file upload; returns data quality inspection report.

### 8. Model Training
- **`POST /model/train`**
- Triggers domain-grouped XGBoost training with baseline comparisons. Protected endpoint.

### 9. Prediction History & Reports
- **`GET /predictions`**: List recent predictions with pagination.
- **`GET /reports/{id}`**: Forensic audit report export for a specific prediction ID.

