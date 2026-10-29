from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    roc_curve,
    confusion_matrix,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

class ModelEvaluator:
    @staticmethod
    def compute_all_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        latency_ms: float = 0.0
    ) -> Dict[str, Any]:
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        fpr = float(fp / (tn + fp)) if (tn + fp) > 0 else 0.0
        fnr = float(fn / (tp + fn)) if (tp + fn) > 0 else 0.0

        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            roc_auc = 0.5

        try:
            p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
            pr_auc = float(auc(r_curve, p_curve))
        except Exception:
            pr_auc = 0.5

        try:
            brier = float(brier_score_loss(y_true, y_prob))
        except Exception:
            brier = 0.0

        # Sample points for ROC curve plotting
        try:
            fpr_arr, tpr_arr, _ = roc_curve(y_true, y_prob)
            step = max(1, len(fpr_arr) // 30)
            roc_points = [
                {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
                for f, t in zip(fpr_arr[::step], tpr_arr[::step])
            ]
            if roc_points[-1]["fpr"] != 1.0:
                roc_points.append({"fpr": 1.0, "tpr": 1.0})
        except Exception:
            roc_points = []

        # Sample points for PR curve plotting
        try:
            p_arr, r_arr, _ = precision_recall_curve(y_true, y_prob)
            step_pr = max(1, len(p_arr) // 30)
            pr_points = [
                {"recall": round(float(r), 4), "precision": round(float(p), 4)}
                for r, p in zip(r_arr[::step_pr], p_arr[::step_pr])
            ]
        except Exception:
            pr_points = []

        # Calibration curve points
        try:
            prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=5, strategy="uniform")
            calibration_points = [
                {"prob_pred": round(float(pred), 4), "prob_true": round(float(true), 4)}
                for pred, true in zip(prob_pred, prob_true)
            ]
        except Exception:
            calibration_points = []

        return {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "specificity": round(spec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "brier_score": round(brier, 4),
            "latency_ms": round(latency_ms, 2),
            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp)
            },
            "roc_curve": roc_points,
            "pr_curve": pr_points,
            "calibration_curve": calibration_points,
            "sample_count": len(y_true),
            "class_distribution": {
                "legitimate": int(np.sum(y_true == 0)),
                "phishing": int(np.sum(y_true == 1))
            }
        }

