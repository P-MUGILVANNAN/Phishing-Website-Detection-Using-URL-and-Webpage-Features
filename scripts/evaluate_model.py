import sys
import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings

def main():
    eval_file = settings.ARTIFACTS_DIR / "evaluation.json"
    meta_file = settings.ARTIFACTS_DIR / "metadata.json"

    if not eval_file.exists() or not meta_file.exists():
        print("Error: No trained model evaluation found. Please run scripts/train_model.py first.")
        sys.exit(1)

    with open(eval_file, "r", encoding="utf-8") as f:
        evaluation = json.load(f)

    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print("=" * 65)
    print("PHISHGUARD AI - COMPREHENSIVE RESEARCH EVALUATION BENCHMARK")
    print("=" * 65)
    print(f"Model Version:         {evaluation.get('model_version')}")
    print(f"Evaluation Protocol:   {evaluation.get('evaluation_protocol')}")
    print(f"Algorithm:             {metadata.get('algorithm')}")
    print(f"Trained At:            {metadata.get('trained_at')}")
    print(f"Total Samples:         {metadata.get('sample_counts', {}).get('total')}")
    print(f"Independent Domains:   {metadata.get('domain_counts', {}).get('train_domains')} Train / {metadata.get('domain_counts', {}).get('test_domains')} Test (Zero Overlap)")
    print("-" * 65)

    main_m = evaluation.get("main_model", {}).get("metrics", {})
    print("MAIN MODEL PERFORMANCE (ON UNSEEN REGISTERED DOMAINS):")
    print(f"  Accuracy:            {main_m.get('accuracy', 0)*100:.2f}%")
    print(f"  Precision:           {main_m.get('precision', 0):.4f}")
    print(f"  Recall/Sensitivity:  {main_m.get('recall', 0):.4f}")
    print(f"  Specificity:         {main_m.get('specificity', 0):.4f}")
    print(f"  F1-Score:            {main_m.get('f1_score', 0):.4f}")
    print(f"  ROC-AUC:             {main_m.get('roc_auc', 0):.4f}")
    print(f"  PR-AUC:              {main_m.get('pr_auc', 0):.4f}")
    print(f"  False Positive Rate: {main_m.get('false_positive_rate', 0):.4f}")
    print(f"  False Negative Rate: {main_m.get('false_negative_rate', 0):.4f}")
    print(f"  Brier Score:         {main_m.get('brier_score', 0):.4f}")
    print(f"  Inference Latency:   {main_m.get('latency_ms', 0):.2f} ms")

    cm = main_m.get("confusion_matrix", {})
    print(f"  Confusion Matrix:    TN={cm.get('tn')}, FP={cm.get('fp')}, FN={cm.get('fn')}, TP={cm.get('tp')}")

    print("-" * 65)
    print("BASELINE COMPARISONS (ON IDENTICAL HELD-OUT UNSEEN DOMAINS):")
    for key, base in evaluation.get("baselines", {}).items():
        b_metrics = base.get("metrics", {})
        print(f"  {base.get('name')}:")
        print(f"    Accuracy: {b_metrics.get('accuracy', 0)*100:.2f}% | F1: {b_metrics.get('f1_score', 0):.4f} | ROC-AUC: {b_metrics.get('roc_auc', 0):.4f}")

    print("-" * 65)
    gen = evaluation.get("generalization_comparison", {})
    print("UNSEEN-DOMAIN GENERALIZATION GAP ANALYSIS:")
    print(f"  Random Split Accuracy (Domain Leakage): {gen.get('random_split_leakage', {}).get('accuracy', 0)*100:.2f}%")
    print(f"  Domain-Grouped Accuracy (True Generalization): {gen.get('domain_grouped_unseen', {}).get('accuracy', 0)*100:.2f}%")
    print(f"  Generalization Gap: {gen.get('generalization_gap_f1', 0):.4f} drop in F1-score on unfamiliar domains.")
    print("=" * 65)

if __name__ == "__main__":
    main()

