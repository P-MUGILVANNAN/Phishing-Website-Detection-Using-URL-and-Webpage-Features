import sys
from pathlib import Path
import pandas as pd

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ml.train import model_trainer

def main():
    data_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "phishguard_research_dataset.csv"
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}. Run scripts/prepare_dataset.py first.")
        sys.exit(1)

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Dataset loaded: {len(df)} samples across multiple registered domains.")

    res = model_trainer.train(
        df=df,
        url_col="url",
        label_col="label",
        html_col="html_text" if "html_text" in df.columns else None,
        test_size=0.20,
        val_size=0.10,
        random_state=42
    )

    print("=" * 60)
    print("PHISHGUARD AI - TRAINING & RESEARCH EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Model Version: {res['model_version']}")
    gen_comp = res["evaluation"]["generalization_comparison"]
    print("\n--- GENERALIZATION & UNSEEN-DOMAIN EVALUATION ---")
    print(f"Domain-Grouped Split (Unseen Domains):")
    print(f"  Accuracy: {gen_comp['domain_grouped_unseen']['accuracy'] * 100:.2f}%")
    print(f"  F1-Score: {gen_comp['domain_grouped_unseen']['f1_score']:.4f}")
    print(f"  ROC-AUC:  {gen_comp['domain_grouped_unseen']['roc_auc']:.4f}")
    print(f"  Domain Leakage Count: {gen_comp['domain_grouped_unseen']['domain_overlap']}")
    print(f"\nRandom Split (Domain Memorization Leakage):")
    print(f"  Accuracy: {gen_comp['random_split_leakage']['accuracy'] * 100:.2f}%")
    print(f"  F1-Score: {gen_comp['random_split_leakage']['f1_score']:.4f}")
    print(f"  ROC-AUC:  {gen_comp['random_split_leakage']['roc_auc']:.4f}")
    print(f"  Domain Leakage Count: {gen_comp['random_split_leakage']['domain_overlap']}")
    print(f"\nGeneralization Gap (F1 Loss on Unseen Domains): {gen_comp['generalization_gap_f1']:.4f}")
    print("=" * 60)
    print("Artifacts saved to backend/artifacts/")

if __name__ == "__main__":
    main()

