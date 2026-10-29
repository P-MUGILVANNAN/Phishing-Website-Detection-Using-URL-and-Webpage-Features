# Processed Datasets

Stores verified, cleaned datasets conforming to the required schema:
- `url`: Normalized or target URL string.
- `label`: Binary classification target (0 = Legitimate, 1 = Phishing).
- `html_text`: (Optional) Visible page text and title context for multi-modal NLP feature generation.

The default curated research benchmark is stored at `phishguard_research_dataset.csv`.

