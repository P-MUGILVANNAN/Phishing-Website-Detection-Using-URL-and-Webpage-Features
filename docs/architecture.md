# PhishGuard AI - System Architecture

## 1. Overview & Dataflow Pipeline

PhishGuard AI provides a production-grade, research-oriented phishing detection architecture designed to prevent training-serving skew, defend against SSRF vulnerabilities during live page inspection, and evaluate model generalization on unseen registered domains.

```
+-------------------------------------------------------------------------+
|                              USER INTERACTION                           |
|       React + TypeScript + Tailwind UI  /  REST API Client              |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        FASTAPI APPLICATION LAYER                        |
|  /api/predict/url | /api/predict/batch | /api/model/train | /api/health |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  INPUT NORMALIZATION & SECURITY LAYER                   |
|  - URLNormalizer: Scheme validation, port stripping, RFC compliance     |
|  - SSRF-Hardened SafeURLFetcher: Private/Loopback/Cloud IP blocking     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        FEATURE EXTRACTION STACK                         |
|  - 32 Lexical & Structural URL features (length, entropy, brand tokens) |
|  - 20 Webpage Structure & NLP Risk Indicators (forms, mismatches, vocab)|
|  Total Feature Dimension: 52 features (Version 1.0.0 Schema)            |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                         MACHINE LEARNING STACK                          |
|  - XGBoost Classifier (with Platt / Sigmoid Probability Calibration)    |
|  - TreeExplainer SHAP attribution & Plain-English observable evidence   |
|  - 3-Class Decision Policy: Legitimate (<0.30), Uncertain, Phishing(≥0.70)
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                       PERSISTENCE & AUDIT LAYER                         |
|  - SQLite Database: PredictionHistory, ModelMetadata, AuditLog          |
|  - Artifact Manifests: model.joblib, evaluation.json, feature_schema.json|
+-------------------------------------------------------------------------+
```

## 2. Server-Side Request Forgery (SSRF) Hardening

Safe webpage analysis is high-risk. PhishGuard AI enforces defense-in-depth:
1. **Pre-Connect DNS Resolution**: Every host is resolved to all associated IPv4/IPv6 addresses before initiating transport.
2. **Strict IP Filtering**: Rejects loopback (`127.0.0.0/8`, `::1`), private RFC-1918/4193 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), multicast, and cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`).
3. **Bounded Redirect Loop**: Automatic client redirects are disabled. Each hop is resolved and re-verified.
4. **Bandwidth & Timeout Caps**: Maximum 512 KB response size, strict 6-second total timeout.
5. **No Script Execution**: JavaScript is never executed; page scripts, forms, and external links are strictly not evaluated.

## 3. Training & Inference Parity

To prevent training-serving skew:
- `PhishGuardPipeline` wraps both the 32 URL features and 20 Webpage/NLP features into an immutable ordered schema (`ALL_FEATURE_NAMES`).
- When webpage HTML is absent or blocked, explicit missing indicators (`page_features_available = 0`) are passed to XGBoost, matching the missing-feature strategy during offline training.
- Versioned schema metadata (`feature_schema.json`) is validated before inference.

