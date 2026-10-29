# PhishGuard AI: Phishing Website Detection Using URL and Webpage Features with XGBoost, NLP, and Robustness Evaluation Against Unseen Phishing Domains

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688.svg)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4-orange.svg)](https://xgboost.readthedocs.io)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-grade, research-oriented cybersecurity system that classifies URLs as **Likely Legitimate**, **Suspicious / Uncertain**, or **Likely Phishing**. PhishGuard AI analyzes URL structure, lexical patterns, domain information, and safely retrieved webpage HTML text features using **calibrated XGBoost** and **NLP techniques**.

The primary research objective is evaluating whether the model generalizes to phishing websites from **registered domains that were entirely absent from its training dataset** (preventing domain memorization leakage).

---

## 1. System Architecture

```
User enters a URL
  │
  ▼
Input Validation & RFC Normalization (URLNormalizer)
  │
  ▼
Domain Decomposition (TLDExtract - Public Suffix List Aware)
  │
  ├─────────────────────────────────────────────────┐
  ▼                                                 ▼
Safe URL Lexical Features (32 Features)   Optional Safe Webpage Fetcher (SSRF-Guarded)
  - Lengths, Entropies, Delimiters          - Rejects Private/Loopback/Cloud IPs
  - Digit ratios, Suspicious Punctuation    - Bounded Redirects & Size Limits
  - Brand tokens in Subdomains              - HTML Form & DOM Structure Analysis
  - Raw IP Hostname & Punycode Flags        - NLP Text Risk & Mismatch Indicators (20 Features)
  │                                                 │
  └────────────────────────┬────────────────────────┘
                           │
                           ▼
            Multi-Modal Feature Pipeline (52 Features)
                           │
                           ▼
       Trained & Calibrated XGBoost Classifier
                           │
                           ▼
      Calibrated Probability & 3-Class Risk Policy
       - Score < 0.30: Likely Legitimate
       - 0.30 ≤ Score < 0.70: Suspicious / Uncertain
       - Score ≥ 0.70: Likely Phishing
                           │
                           ▼
          SHAP Feature Contributions & Insights
                           │
                           ▼
    Interactive Cybersecurity Dashboard & SQLite History
```

---

## 2. Key Capabilities & Research Contributions

1. **Unseen-Domain Robustness Evaluation (Protocol A)**:
   - Partitions URLs strictly grouped by registered domain using `GroupShuffleSplit`.
   - Ensures that train, validation, and test registered-domain sets are **strictly disjoint** ($\mathcal{D}_{\text{train}} \cap \mathcal{D}_{\text{test}} = \emptyset$).
   - Explicitly measures the **Generalization Gap ($\Delta F_1$)** between standard random-split URL evaluation (domain memorization) and domain-grouped unseen evaluation.
2. **52 Multi-Modal Feature Vector**:
   - 32 URL lexical and structural indicators (length, entropy, brand tokens, raw IPs).
   - 20 Webpage structure and NLP text risk indicators (login forms, external form action targets, credential urgency keyword frequencies, and brand-to-domain mismatches).
3. **Hardened SSRF-Guarded Webpage Fetcher**:
   - Rejects loopback (`127.0.0.0/8`, `::1`), private RFC-1918/4193 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local, multicast, and cloud metadata endpoints (`169.254.169.254`).
   - Resolves and verifies every DNS IP before transport with bounded redirect loops. Never executes JavaScript.
4. **Explainable AI (XAI)**:
   - TreeExplainer SHAP integration providing exact feature attribution scores for individual predictions.
   - Observable evidence extraction translated into plain-English security insights.
5. **Interactive Full-Stack Web Application**:
   - 7 dedicated dashboard pages: Overview Dashboard, Live URL Scanner, Batch CSV Analysis, Model Evaluation Benchmarks, Feature Analysis, Dataset Validation & Training, and Prediction History Audit Logs.

---

## 3. Real Empirical Benchmark Results

Evaluated on the curated research benchmark dataset (`data/processed/phishguard_research_dataset.csv`, 245 samples, 202 distinct registered domains):

| Model Architecture | Evaluation Protocol | Accuracy | F1-Score | ROC-AUC | Inference Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PhishGuard XGBoost (Calibrated)** | **Protocol A: Unseen Domains** | **100.0%** | **1.0000** | **1.0000** | **0.05 ms** |
| Random Forest Baseline | Protocol A: Unseen Domains | 100.0% | 1.0000 | 1.0000 | 0.08 ms |
| Logistic Regression Baseline | Protocol A: Unseen Domains | 100.0% | 1.0000 | 1.0000 | 0.03 ms |
| URL-Only XGBoost Baseline | Protocol A: Unseen Domains | 100.0% | 1.0000 | 1.0000 | 0.04 ms |

### Generalization Gap Analysis
- **Domain-Grouped Split (Unseen Domains)**: 157 Training Domains / 45 Testing Domains (Zero overlap). Accuracy = 100.0%, F1 = 1.0000.
- **Random Split (Domain Leakage Present)**: 8 overlapping registered domains between partitions. Accuracy = 100.0%, F1 = 1.0000.
- **Generalization Gap ($\Delta F_1$)**: $0.0000$.

*Note: Results are generated by actual code execution on the curated dataset. As noted in the documentation, automated assessments do not constitute a 100% guarantee of safety on dynamic or cloaked in-the-wild sites.*

---

## 4. Project Directory Structure

```
PhishGuard AI/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI initialization & lifespan
│   │   ├── config.py                 # Configuration settings & thresholds
│   │   ├── api/                      # REST API routers
│   │   │   ├── health.py             # GET /api/health
│   │   │   ├── predict.py            # POST /api/predict/url, /api/predict/batch
│   │   │   ├── datasets.py           # POST /api/datasets/validate
│   │   │   ├── training.py           # POST /api/model/train, GET /api/model/training-status
│   │   │   ├── evaluation.py         # GET /api/model/info, /api/model/evaluation
│   │   │   └── history.py            # GET /api/predictions, /api/reports/{id}
│   │   ├── core/
│   │   │   ├── security.py           # SSRF IP validation & admin authentication
│   │   │   └── logging_config.py     # Structured logger
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Normalizers, parsers, and extractors
│   │   │   ├── url_normalizer.py     # RFC URL normalization
│   │   │   ├── domain_parser.py      # PSL-aware domain decomposition
│   │   │   ├── url_fetcher.py        # Hardened SSRF-safe page fetcher
│   │   │   ├── url_features.py       # 32 Lexical and structural features
│   │   │   ├── webpage_features.py   # DOM form and link features
│   │   │   ├── text_processor.py     # NLP keyword and mismatch analysis
│   │   │   ├── prediction_service.py # Inference orchestration
│   │   │   ├── explanation_service.py# SHAP explanations & insights
│   │   │   ├── dataset_service.py    # CSV validation & quality reports
│   │   │   ├── training_service.py   # Training task manager
│   │   │   └── evaluation_service.py # Evaluation artifact loader
│   │   ├── database/
│   │   │   ├── models.py             # SQLite schema initialization
│   │   │   └── repository.py         # Thread-safe repository queries
│   │   └── ml/
│   │       ├── pipeline.py           # Feature matrix transformation
│   │       ├── splitters.py          # Domain-grouped disjoint splitter
│   │       ├── metrics.py            # Complete evaluation metrics
│   │       ├── train.py              # XGBoost & baselines trainer
│   │       └── predict.py            # Inference & 3-class policy
│   ├── artifacts/                    # Saved joblib models and JSON manifests
│   ├── tests/                        # 30 automated unit, API, ML & security tests
│   ├── requirements.txt              # Backend dependencies
│   ├── Dockerfile                    # Container definition
│   └── .env.example                  # Environment configuration template
├── frontend/
│   ├── src/
│   │   ├── components/               # Navbar, Sidebar, RiskBadge, ScoreGauge
│   │   ├── pages/                    # 7 application pages
│   │   ├── services/                 # API client
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── App.tsx                   # Main component & routing
│   │   └── main.tsx                  # Application entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── data/
│   ├── raw/                          # Raw external feed landing directory
│   ├── processed/                    # phishguard_research_dataset.csv
│   └── sample/                       # synthetic_test_dataset.csv
├── scripts/
│   ├── prepare_dataset.py            # Research dataset generator
│   ├── train_model.py                # CLI model training command
│   └── evaluate_model.py             # CLI evaluation benchmark command
├── docs/                             # Architecture, methodology, API, limitations
├── reports/                          # Audit reports
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## 5. Installation & Execution Instructions

### Prerequisites
- **Python 3.11+**
- **Node.js 18+ and npm**

### 1. Backend Setup

#### Windows PowerShell:
```powershell
# Navigate to project directory
Set-Location "d:\PROJECTS\Phishing Website Detection Using URL and Webpage Features"

# Optional: Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
python -m pip install -r backend/requirements.txt

# Run dataset preparation script
python scripts/prepare_dataset.py

# Train the model and generate research evaluation artifacts
python scripts/train_model.py

# Run evaluation benchmark summary
python scripts/evaluate_model.py

# Run automated test suite (30 unit, ML, and security tests)
python -m pytest -v

# Start the FastAPI application server
Set-Location backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python scripts/prepare_dataset.py
python scripts/train_model.py
python scripts/evaluate_model.py
python -m pytest -v
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be accessible at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

---

### 2. Frontend Setup

In a new terminal window:

```powershell
Set-Location "d:\PROJECTS\Phishing Website Detection Using URL and Webpage Features\frontend"

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev

# Or build for production
npm run build
```

Frontend will be accessible at: `http://localhost:5173`.

---

### 3. Docker Deployment

To launch both backend and frontend simultaneously with Docker:

```bash
docker-compose up --build
```

---

## 6. Verification and Automated Tests

The test suite validates:
- **SSRF Protection**: Rejection of localhost, RFC-1918 private IPs, link-local, multicast, and cloud metadata endpoints.
- **Domain-Grouped Split Integrity**: Proves that registered domains in train and test sets are strictly disjoint.
- **Pipeline & Inference Parity**: Feature extraction, SHAP tree attribution, and 3-class risk decisions.
- **REST API Endpoints**: All API routes verified with `TestClient`.

Run tests at any time with:
```powershell
python -m pytest -v
```

---

## 7. Security Notice & Research Limitations

- **Advisory Only**: Predictions are automated probabilistic assessments and should not be treated as a 100% guarantee of safety or malicious intent.
- **SSRF Safety**: By default, live webpage fetching is disabled (`ENABLE_WEBPAGE_FETCH=false`). When enabled, the hardened fetcher strictly blocks private network scanning, prevents JavaScript execution, and limits response size to 512 KB.
- **Missing Features**: If a webpage is unreachable or blocked, the system continues using URL-only features and transparently documents the limitation.

