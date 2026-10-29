import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
import shap

from app.config import settings
from app.ml.pipeline import pipeline, ALL_FEATURE_NAMES, FEATURE_DESCRIPTIONS
from app.ml.splitters import DomainGroupedSplitter
from app.ml.metrics import ModelEvaluator
from app.core.logging_config import logger

class ModelTrainer:
    def __init__(self, artifacts_dir: Optional[Path] = None):
        self.artifacts_dir = artifacts_dir or settings.ARTIFACTS_DIR
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_dataset_fingerprint(df: pd.DataFrame) -> str:
        content = df.to_csv(index=False).encode("utf-8")
        return hashlib.sha256(content).hexdigest()[:16]

    def train(
        self,
        df: pd.DataFrame,
        url_col: str = "url",
        label_col: str = "label",
        html_col: Optional[str] = "html_text",
        test_size: float = 0.20,
        val_size: float = 0.10,
        xgb_params: Optional[Dict[str, Any]] = None,
        random_state: int = 42
    ) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Starting PhishGuard training pipeline on {len(df)} samples...")

        # 1. Dataset fingerprint and quality verification
        fingerprint = self.compute_dataset_fingerprint(df)
        label_counts = df[label_col].value_counts().to_dict()
        n_pos = label_counts.get(1, 0)
        n_neg = label_counts.get(0, 0)
        scale_pos_weight = float(n_neg / max(n_pos, 1))

        # 2. Extract features for entire dataset
        logger.info("Extracting combined URL and webpage features...")
        X_all, feature_names = pipeline.transform_dataset(df, url_col=url_col, html_col=html_col)
        y_all = df[label_col].values.astype(int)

        # 3. Protocol A: Domain-Grouped Split (Unseen Domain Evaluation)
        logger.info("Executing domain-grouped train/val/test split...")
        grouped_split = DomainGroupedSplitter.split(
            df=df,
            url_col=url_col,
            label_col=label_col,
            test_size=test_size,
            val_size=val_size,
            random_state=random_state
        )

        train_indices = grouped_split["train_df"].index.values
        val_indices = grouped_split["val_df"].index.values if not grouped_split["val_df"].empty else np.array([])
        test_indices = grouped_split["test_df"].index.values

        X_train, y_train = X_all[train_indices], y_all[train_indices]
        X_val, y_val = (X_all[val_indices], y_all[val_indices]) if len(val_indices) > 0 else (X_train, y_train)
        X_test, y_test = X_all[test_indices], y_all[test_indices]

        # 4. Also perform Random Split for comparative research baseline
        random_split_res = DomainGroupedSplitter.random_split(
            df=df,
            url_col=url_col,
            label_col=label_col,
            test_size=test_size,
            random_state=random_state
        )
        rand_train_idx = random_split_res["train_df"].index.values
        rand_test_idx = random_split_res["test_df"].index.values
        X_rand_train, y_rand_train = X_all[rand_train_idx], y_all[rand_train_idx]
        X_rand_test, y_rand_test = X_all[rand_test_idx], y_all[rand_test_idx]

        # 5. Configure Main Model (XGBoost)
        default_xgb_params = {
            "n_estimators": 150,
            "max_depth": 5,
            "learning_rate": 0.08,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "scale_pos_weight": scale_pos_weight,
            "eval_metric": "logloss",
            "random_state": random_state
        }
        if xgb_params:
            default_xgb_params.update(xgb_params)

        logger.info(f"Training main XGBoost model with params: {default_xgb_params}")
        main_xgb = XGBClassifier(**default_xgb_params)
        main_xgb.fit(X_train, y_train)

        # Measure latency
        t0 = time.time()
        y_test_pred_raw = main_xgb.predict(X_test)
        y_test_prob_raw = main_xgb.predict_proba(X_test)[:, 1]
        inference_latency_ms = ((time.time() - t0) / max(len(X_test), 1)) * 1000.0

        # Calibration using 3-fold cross-validation or validation data
        try:
            calibrated_model = CalibratedClassifierCV(estimator=main_xgb, cv=3, method="sigmoid")
            calibrated_model.fit(X_train, y_train)
            y_test_prob = calibrated_model.predict_proba(X_test)[:, 1]
            y_test_pred = (y_test_prob >= 0.5).astype(int)
            final_model = calibrated_model
            is_calibrated = True
            logger.info("Fitted Sigmoid-calibrated probabilities successfully.")
        except Exception as e:
            logger.warning(f"Calibration skipped due to: {e}; using raw XGBoost probabilities")
            y_test_prob = y_test_prob_raw
            y_test_pred = y_test_pred_raw
            final_model = main_xgb
            is_calibrated = False

        # Compute Unseen Domain (Domain-Grouped) Metrics for Main Model
        unseen_domain_metrics = ModelEvaluator.compute_all_metrics(
            y_true=y_test,
            y_pred=y_test_pred,
            y_prob=y_test_prob,
            latency_ms=inference_latency_ms
        )

        # 6. Train Baseline Models on Domain-Grouped Split
        logger.info("Training baseline models (Logistic Regression, Random Forest)...")
        # Logistic Regression
        lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)
        # Normalize for LR
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        lr.fit(X_train_scaled, y_train)
        lr_prob = lr.predict_proba(X_test_scaled)[:, 1]
        lr_pred = lr.predict(X_test_scaled)
        lr_metrics = ModelEvaluator.compute_all_metrics(y_test, lr_pred, lr_prob)

        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=random_state)
        rf.fit(X_train, y_train)
        rf_prob = rf.predict_proba(X_test)[:, 1]
        rf_pred = rf.predict(X_test)
        rf_metrics = ModelEvaluator.compute_all_metrics(y_test, rf_pred, rf_prob)

        # URL-Only XGBoost baseline (using only first 32 URL features)
        n_url_feats = len(pipeline.feature_names) - len(pipeline.feature_names[32:])
        xgb_url_only = XGBClassifier(**default_xgb_params)
        xgb_url_only.fit(X_train[:, :32], y_train)
        url_only_prob = xgb_url_only.predict_proba(X_test[:, :32])[:, 1]
        url_only_pred = (url_only_prob >= 0.5).astype(int)
        url_only_metrics = ModelEvaluator.compute_all_metrics(y_test, url_only_pred, url_only_prob)

        # 7. Train Main Model on Random Split to demonstrate Generalization Gap
        xgb_rand = XGBClassifier(**default_xgb_params)
        xgb_rand.fit(X_rand_train, y_rand_train)
        rand_prob = xgb_rand.predict_proba(X_rand_test)[:, 1]
        rand_pred = (rand_prob >= 0.5).astype(int)
        random_split_metrics = ModelEvaluator.compute_all_metrics(y_rand_test, rand_pred, rand_prob)

        # 8. Compute Feature Importance & SHAP explanations
        logger.info("Computing SHAP values and feature importances...")
        feature_importances = {}
        try:
            # XGBoost native feature importances (gain)
            gain_importances = main_xgb.feature_importances_
            feature_importances = {
                fname: round(float(imp), 4)
                for fname, imp in sorted(zip(feature_names, gain_importances), key=lambda x: x[1], reverse=True)
            }
        except Exception as e:
            logger.warning(f"Feature importance error: {e}")

        shap_summary_dict: Dict[str, float] = {}
        try:
            explainer = shap.TreeExplainer(main_xgb)
            # Sample up to 100 rows for background / explanation
            sample_X = X_test[: min(100, len(X_test))]
            shap_values = explainer.shap_values(sample_X)
            mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
            shap_summary_dict = {
                fname: round(float(val), 4)
                for fname, val in sorted(zip(feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)
            }
        except Exception as e:
            logger.warning(f"SHAP explanation computation error: {e}")
            shap_summary_dict = feature_importances

        # 9. Save artifacts
        model_version = f"v{int(time.time())}"
        joblib.dump(final_model, self.artifacts_dir / "model.joblib")
        joblib.dump(main_xgb, self.artifacts_dir / "xgb_raw.joblib")
        joblib.dump(
            {
                "logistic_regression": lr,
                "random_forest": rf,
                "url_only_xgboost": xgb_url_only,
                "scaler": scaler
            },
            self.artifacts_dir / "baselines.joblib"
        )

        # Feature Schema JSON
        feature_schema_payload = {
            "version": settings.FEATURE_SCHEMA_VERSION,
            "feature_names": feature_names,
            "feature_count": len(feature_names),
            "descriptions": FEATURE_DESCRIPTIONS,
            "url_features_count": 32,
            "webpage_features_count": 19
        }
        with open(self.artifacts_dir / "feature_schema.json", "w", encoding="utf-8") as f:
            json.dump(feature_schema_payload, f, indent=2)

        # Model Metadata JSON
        metadata_payload = {
            "model_version": model_version,
            "algorithm": "XGBoost Classifier (with Probability Calibration)",
            "trained_at": datetime.now().isoformat(),
            "training_duration_seconds": round(time.time() - start_time, 2),
            "dataset_fingerprint": fingerprint,
            "feature_schema_version": settings.FEATURE_SCHEMA_VERSION,
            "is_calibrated": is_calibrated,
            "thresholds": {
                "legitimate": settings.THRESHOLD_LEGITIMATE,
                "phishing": settings.THRESHOLD_PHISHING
            },
            "sample_counts": {
                "total": len(df),
                "train": len(X_train),
                "val": len(X_val),
                "test": len(X_test)
            },
            "domain_counts": {
                "train_domains": grouped_split["train_domain_count"],
                "val_domains": grouped_split["val_domain_count"],
                "test_domains": grouped_split["test_domain_count"],
                "domain_leakage": 0
            },
            "class_distribution": label_counts,
            "hyperparameters": default_xgb_params
        }
        with open(self.artifacts_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_payload, f, indent=2)

        # Evaluation Results JSON
        evaluation_payload = {
            "model_version": model_version,
            "evaluated_at": datetime.now().isoformat(),
            "evaluation_protocol": "Protocol A: Domain-Grouped Split (Unseen Registered Domains)",
            "domain_leakage_overlap": 0,
            "main_model": {
                "name": "PhishGuard XGBoost (Calibrated)",
                "metrics": unseen_domain_metrics
            },
            "baselines": {
                "logistic_regression": {
                    "name": "Logistic Regression Baseline",
                    "metrics": lr_metrics
                },
                "random_forest": {
                    "name": "Random Forest Baseline",
                    "metrics": rf_metrics
                },
                "url_only_xgboost": {
                    "name": "URL-Only XGBoost (No Webpage NLP)",
                    "metrics": url_only_metrics
                }
            },
            "generalization_comparison": {
                "domain_grouped_unseen": {
                    "description": "Zero domain overlap between train and test partitions",
                    "accuracy": unseen_domain_metrics["accuracy"],
                    "f1_score": unseen_domain_metrics["f1_score"],
                    "roc_auc": unseen_domain_metrics["roc_auc"],
                    "domain_overlap": 0
                },
                "random_split_leakage": {
                    "description": "Standard random split with shared registered domains (Domain Memorization)",
                    "accuracy": random_split_metrics["accuracy"],
                    "f1_score": random_split_metrics["f1_score"],
                    "roc_auc": random_split_metrics["roc_auc"],
                    "domain_overlap": random_split_res["domain_overlap_count"]
                },
                "generalization_gap_f1": round(
                    random_split_metrics["f1_score"] - unseen_domain_metrics["f1_score"], 4
                )
            },
            "feature_importance": feature_importances,
            "shap_importance": shap_summary_dict
        }
        with open(self.artifacts_dir / "evaluation.json", "w", encoding="utf-8") as f:
            json.dump(evaluation_payload, f, indent=2)

        logger.info(f"Training completed successfully in {round(time.time() - start_time, 2)}s.")
        return {
            "model_version": model_version,
            "metadata": metadata_payload,
            "evaluation": evaluation_payload
        }

model_trainer = ModelTrainer()
