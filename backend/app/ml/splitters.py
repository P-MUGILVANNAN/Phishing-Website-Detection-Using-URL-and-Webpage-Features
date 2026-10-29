from typing import Tuple, List, Set, Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from app.services.domain_parser import domain_parser

class DomainGroupedSplitter:
    @staticmethod
    def extract_registered_domains(urls: List[str]) -> List[str]:
        domains = []
        for u in urls:
            parsed = domain_parser.parse(u)
            reg = parsed.registered_domain if parsed.registered_domain else u
            domains.append(reg.lower())
        return domains

    @classmethod
    def split(
        cls,
        df: pd.DataFrame,
        url_col: str = "url",
        label_col: str = "label",
        test_size: float = 0.20,
        val_size: float = 0.10,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Splits dataset by grouping URLs by their registered domains.
        Guarantees that train, val, and test sets have DISJOINT sets of registered domains.
        """
        if "registered_domain" not in df.columns:
            domains = cls.extract_registered_domains(df[url_col].tolist())
            df = df.copy()
            df["registered_domain"] = domains
        else:
            df = df.copy()

        groups = df["registered_domain"].values
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
        train_val_idx, test_idx = next(gss.split(df, df[label_col], groups=groups))

        train_val_df = df.iloc[train_val_idx].copy()
        test_df = df.iloc[test_idx].copy()

        # Split train_val into train and validation
        if val_size > 0:
            adjusted_val_size = val_size / (1.0 - test_size)
            gss_val = GroupShuffleSplit(n_splits=1, test_size=adjusted_val_size, random_state=random_state)
            train_idx, val_idx = next(gss_val.split(
                train_val_df,
                train_val_df[label_col],
                groups=train_val_df["registered_domain"].values
            ))
            train_df = train_val_df.iloc[train_idx].copy()
            val_df = train_val_df.iloc[val_idx].copy()
        else:
            train_df = train_val_df
            val_df = pd.DataFrame()

        train_domains = set(train_df["registered_domain"].unique())
        test_domains = set(test_df["registered_domain"].unique())
        val_domains = set(val_df["registered_domain"].unique()) if not val_df.empty else set()

        # Strict disjointness assertions
        overlap_train_test = train_domains.intersection(test_domains)
        overlap_train_val = train_domains.intersection(val_domains)
        overlap_val_test = val_domains.intersection(test_domains)

        if overlap_train_test:
            raise ValueError(f"Domain leakage detected between train and test: {len(overlap_train_test)} shared domains!")
        if overlap_train_val:
            raise ValueError(f"Domain leakage detected between train and validation: {len(overlap_train_val)} shared domains!")
        if overlap_val_test:
            raise ValueError(f"Domain leakage detected between validation and test: {len(overlap_val_test)} shared domains!")

        return {
            "train_df": train_df,
            "val_df": val_df,
            "test_df": test_df,
            "train_domains": list(train_domains),
            "val_domains": list(val_domains),
            "test_domains": list(test_domains),
            "train_domain_count": len(train_domains),
            "val_domain_count": len(val_domains),
            "test_domain_count": len(test_domains),
            "train_sample_count": len(train_df),
            "val_sample_count": len(val_df),
            "test_sample_count": len(test_df),
            "train_label_dist": train_df[label_col].value_counts().to_dict(),
            "val_label_dist": val_df[label_col].value_counts().to_dict() if not val_df.empty else {},
            "test_label_dist": test_df[label_col].value_counts().to_dict(),
            "domain_overlap_count": 0
        }

    @classmethod
    def random_split(
        cls,
        df: pd.DataFrame,
        url_col: str = "url",
        label_col: str = "label",
        test_size: float = 0.20,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Standard random stratified split (used as baseline to demonstrate domain leakage gap).
        """
        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            stratify=df[label_col],
            random_state=random_state
        )
        if "registered_domain" not in df.columns:
            train_domains = set(cls.extract_registered_domains(train_df[url_col].tolist()))
            test_domains = set(cls.extract_registered_domains(test_df[url_col].tolist()))
        else:
            train_domains = set(train_df["registered_domain"].unique())
            test_domains = set(test_df["registered_domain"].unique())

        overlap = train_domains.intersection(test_domains)

        return {
            "train_df": train_df,
            "test_df": test_df,
            "train_domains_count": len(train_domains),
            "test_domains_count": len(test_domains),
            "domain_overlap_count": len(overlap),
            "overlapping_domains_sample": list(overlap)[:10]
        }

