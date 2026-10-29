import pytest
import pandas as pd
from app.ml.splitters import DomainGroupedSplitter

def test_domain_grouped_split_strictly_disjoint():
    # Construct dataframe with overlapping URLs from multiple domains
    data = [
        {"url": "https://google.com/a", "label": 0},
        {"url": "https://google.com/b", "label": 0},
        {"url": "https://google.com/c", "label": 0},
        {"url": "https://github.com/a", "label": 0},
        {"url": "https://github.com/b", "label": 0},
        {"url": "https://python.org/a", "label": 0},
        {"url": "https://apple.com/a", "label": 0},
        {"url": "http://fake-paypal-1.com/login", "label": 1},
        {"url": "http://fake-paypal-1.com/verify", "label": 1},
        {"url": "http://fake-chase-2.com/auth", "label": 1},
        {"url": "http://fake-apple-3.com/id", "label": 1},
        {"url": "http://fake-netflix-4.com/renew", "label": 1},
    ]
    df = pd.DataFrame(data)

    res = DomainGroupedSplitter.split(df, test_size=0.25, val_size=0.0, random_state=42)

    train_domains = set(res["train_domains"])
    test_domains = set(res["test_domains"])

    # Core research assertion: train and test registered domains must be DISJOINT
    intersection = train_domains.intersection(test_domains)
    assert len(intersection) == 0, f"Domain leakage detected: {intersection}"
    assert res["domain_overlap_count"] == 0
    assert len(res["train_df"]) > 0
    assert len(res["test_df"]) > 0

