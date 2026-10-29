# PhishGuard AI - Dataset Guide

## 1. Supported Formats & Sourcing

PhishGuard AI supports CSV datasets containing URL security samples.

### Accepted Column Configurations
- `url, label`: Minimal binary classification dataset.
- `url, label, html_text`: Multi-modal dataset including visible page text and document title.
- `url, domain, label, page_title, html_text`: Extended attribute dataset.

### Label Mapping Conventions
The system supports flexible binary mappings:
- `0`: Legitimate, Benign, Safe, Good
- `1`: Phishing, Malicious, Suspicious, Bad

Custom mappings can also be specified via the API or dashboard.

## 2. Research Data Sources

Recommended authorized open-source feeds for research and academic evaluation:
1. **Tranco List**: Research-oriented top sites ranking providing representative legitimate domain distributions without ad-tracker bias.
2. **PhishTank**: Community-verified phishing URL feed providing targeted brand names and submission timestamps.
3. **OpenPhish**: Real-time phishing threat feed.
4. **URLhaus**: Malware and phishing distribution URLs curated by abuse.ch.

Always verify licensing and collection timestamps before aggregating feeds.

## 3. Data Quality & Preprocessing Checks

Before initiating model training, the dataset undergoes automated quality validation:
- **Missing Value Check**: Drops empty URLs or undefined labels.
- **URL Syntax Validation**: Parses hostnames, schemes, and path tokens using RFC specifications.
- **De-duplication**: Removes duplicate URL records.
- **Conflicting Label Resolution**: Detects and purges URLs assigned conflicting labels.
- **Imbalance Calculation**: Computes class ratios to configure XGBoost `scale_pos_weight`.
- **Domain Cardinality**: Groups URLs by registered domain to establish disjoint partitions.

