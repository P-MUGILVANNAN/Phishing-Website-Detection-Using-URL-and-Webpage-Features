import io
import re
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from app.services.url_normalizer import URLNormalizer
from app.services.domain_parser import domain_parser

DEFAULT_LABEL_MAPPING = {
    "0": 0,
    "1": 1,
    "0.0": 0,
    "1.0": 1,
    "legitimate": 0,
    "benign": 0,
    "good": 0,
    "phishing": 1,
    "malicious": 1,
    "bad": 1
}

class DatasetService:
    @classmethod
    def validate_and_parse_csv(
        cls,
        csv_content: str,
        url_col: str = "url",
        label_col: str = "label",
        html_col: Optional[str] = "html_text",
        custom_label_map: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Validates CSV dataset structure, cleans data, checks class balance,
        and generates a detailed data-quality report.
        """
        try:
            df = pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            return {
                "is_valid": False,
                "error_message": f"Malformed CSV file: {str(e)}",
                "quality_report": None,
                "clean_df": None
            }

        # Normalize column names for matching
        col_map = {c.strip().lower(): c for c in df.columns}
        
        target_url_col = None
        target_label_col = None
        target_html_col = None

        # Resolve URL column
        for cand in [url_col.lower(), "url", "urls", "website", "domain"]:
            if cand in col_map:
                target_url_col = col_map[cand]
                break

        # Resolve Label column
        for cand in [label_col.lower(), "label", "labels", "class", "target", "status", "result"]:
            if cand in col_map:
                target_label_col = col_map[cand]
                break

        # Resolve optional HTML column
        if html_col:
            for cand in [html_col.lower(), "html_text", "html", "page_text", "text", "page_title"]:
                if cand in col_map:
                    target_html_col = col_map[cand]
                    break

        if not target_url_col or not target_label_col:
            return {
                "is_valid": False,
                "error_message": f"Missing required columns. Found: {list(df.columns)}. Need URL and Label columns.",
                "quality_report": None,
                "clean_df": None
            }

        initial_row_count = len(df)
        missing_urls = int(df[target_url_col].isna().sum())
        missing_labels = int(df[target_label_col].isna().sum())

        # Drop missing
        df_clean = df.dropna(subset=[target_url_col, target_label_col]).copy()
        
        # Check label mapping
        label_map = custom_label_map or DEFAULT_LABEL_MAPPING
        def map_label(val):
            s_val = str(val).strip().lower()
            return label_map.get(s_val, None)

        df_clean["_mapped_label"] = df_clean[target_label_col].apply(map_label)
        unmapped_labels = int(df_clean["_mapped_label"].isna().sum())
        df_clean = df_clean.dropna(subset=["_mapped_label"]).copy()
        df_clean["_mapped_label"] = df_clean["_mapped_label"].astype(int)

        # Validate URLs
        valid_urls_mask = []
        domains = []
        for u in df_clean[target_url_col]:
            norm = URLNormalizer.normalize(str(u))
            valid_urls_mask.append(norm.is_valid)
            parsed_d = domain_parser.parse(norm.hostname or str(u))
            domains.append(parsed_d.registered_domain or norm.hostname or "unknown")

        invalid_urls_count = int(sum(not v for v in valid_urls_mask))
        df_clean = df_clean[valid_urls_mask].copy()
        df_clean["registered_domain"] = [d for d, v in zip(domains, valid_urls_mask) if v]

        # Duplicate checking
        duplicate_urls_count = int(df_clean.duplicated(subset=[target_url_col]).sum())
        # Conflicting labels check: same URL with different labels
        conflict_groups = df_clean.groupby(target_url_col)["_mapped_label"].nunique()
        conflicting_urls_count = int((conflict_groups > 1).sum())

        # Deduplicate
        df_clean = df_clean.drop_duplicates(subset=[target_url_col], keep="first")

        # Class counts
        label_counts = df_clean["_mapped_label"].value_counts().to_dict()
        legit_count = label_counts.get(0, 0)
        phish_count = label_counts.get(1, 0)
        total_clean = len(df_clean)

        imbalance_ratio = round(max(legit_count, phish_count) / max(min(legit_count, phish_count), 1), 2)
        unique_domains_count = int(df_clean["registered_domain"].nunique())

        has_html_data = bool(target_html_col and target_html_col in df_clean.columns)

        quality_report = {
            "initial_row_count": initial_row_count,
            "clean_row_count": total_clean,
            "missing_urls": missing_urls,
            "missing_labels": missing_labels,
            "unmapped_labels": unmapped_labels,
            "invalid_urls": invalid_urls_count,
            "duplicate_urls": duplicate_urls_count,
            "conflicting_labels": conflicting_urls_count,
            "unique_domains_count": unique_domains_count,
            "class_distribution": {
                "legitimate (0)": legit_count,
                "phishing (1)": phish_count
            },
            "class_imbalance_ratio": imbalance_ratio,
            "has_webpage_text_column": has_html_data,
            "identified_columns": {
                "url": target_url_col,
                "label": target_label_col,
                "html": target_html_col
            }
        }

        # Form standard dataframe for pipeline
        standard_df = pd.DataFrame({
            "url": df_clean[target_url_col],
            "label": df_clean["_mapped_label"],
            "registered_domain": df_clean["registered_domain"]
        })
        if has_html_data:
            standard_df["html_text"] = df_clean[target_html_col]

        return {
            "is_valid": total_clean > 10,
            "error_message": None if total_clean > 10 else "Dataset contains fewer than 10 valid records after cleaning.",
            "quality_report": quality_report,
            "clean_df": standard_df
        }

dataset_service = DatasetService()

