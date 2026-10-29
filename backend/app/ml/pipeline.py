import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import joblib

from app.services.url_features import url_feature_extractor, URLFeatureExtractor
from app.services.webpage_features import webpage_feature_extractor, WebpageFeatureExtractor
from app.services.domain_parser import domain_parser

ALL_FEATURE_NAMES: List[str] = (
    URLFeatureExtractor.FEATURE_NAMES + WebpageFeatureExtractor.FEATURE_NAMES
)

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # URL Features
    "url_length": "Total character length of the normalized URL",
    "hostname_length": "Character length of the hostname",
    "registered_domain_length": "Character length of the registered domain",
    "path_length": "Length of the URL path",
    "query_length": "Length of the query string parameters",
    "count_dots": "Number of dot characters (.) in the URL",
    "count_hyphens": "Number of hyphen characters (-) in the URL",
    "count_underscores": "Number of underscore characters (_) in the URL",
    "count_slashes": "Number of forward slashes (/) in the URL",
    "count_question_marks": "Number of question mark delimiters (?)",
    "count_equals": "Number of equal signs (=) in parameters",
    "count_ampersands": "Number of parameter delimiters (&)",
    "count_percent": "Number of percent characters (%) indicating URL encoding",
    "count_digits": "Total count of numeric digit characters in URL",
    "digit_ratio": "Proportion of numeric digits to total URL length",
    "subdomain_depth": "Depth of subdomains preceding registered domain",
    "num_parameters": "Number of query string parameters",
    "num_path_segments": "Count of path hierarchy directories",
    "suspicious_punctuation_count": "Count of consecutive suspicious punctuations (e.g. //, --, ..)",
    "has_ip_hostname": "Flag indicating if hostname is a raw IPv4/IPv6 address",
    "has_at_symbol": "Flag indicating presence of credentials delimiter (@)",
    "has_nonstandard_port": "Flag indicating non-standard HTTP/HTTPS port",
    "has_fragment": "Flag indicating presence of anchor fragment (#)",
    "is_https": "Flag indicating HTTPS protocol usage",
    "is_punycode": "Flag indicating internationalized domain (IDN / xn--)",
    "has_encoded_chars": "Flag indicating presence of hex-encoded characters",
    "has_suspicious_words_hostname": "Flag indicating deceptive security terms in hostname",
    "suspicious_words_count": "Frequency of deceptive security terms in hostname",
    "has_brand_in_subdomain": "Flag indicating known brand token found in subdomain",
    "brand_in_subdomain_count": "Count of popular brand tokens in subdomain",
    "hostname_entropy": "Shannon entropy score of the hostname character distribution",
    "path_entropy": "Shannon entropy score of the URL path character distribution",
    # Webpage & NLP Features
    "page_features_available": "Flag indicating whether webpage HTML was retrieved and analyzed",
    "title_length": "Character length of the HTML document title",
    "text_length": "Character length of sanitized visible text",
    "num_forms": "Total number of interactive HTML forms",
    "num_password_inputs": "Count of sensitive password input fields",
    "num_external_links": "Count of hyperlinks pointing to external domains",
    "num_internal_links": "Count of hyperlinks pointing within the same domain",
    "num_iframes": "Count of embedded HTML iframes",
    "num_scripts": "Count of client-side JavaScript script tags",
    "has_login_form": "Indicator of login or credential entry form",
    "num_hidden_inputs": "Count of hidden form input fields",
    "external_resource_ratio": "Proportion of external links to total links",
    "has_external_form_action": "High-risk flag: form action posts to a foreign domain",
    "login_keyword_freq": "Occurrences of login/sign-in keywords in visible text",
    "verify_keyword_freq": "Occurrences of account verification/suspension keywords",
    "pw_reset_keyword_freq": "Occurrences of password reset keywords",
    "financial_keyword_freq": "Occurrences of payment, banking, or credit card keywords",
    "urgency_keyword_freq": "Occurrences of artificial urgency phrases (e.g. within 24 hours)",
    "brand_impersonation_count": "Count of brand names in text not matching registered domain",
    "title_domain_mismatch": "High-risk indicator: page title claims a brand foreign to domain"
}

class PhishGuardPipeline:
    def __init__(self, feature_names: Optional[List[str]] = None):
        self.feature_names = feature_names or ALL_FEATURE_NAMES
        self.version = "1.0.0"

    def extract_features_single(
        self,
        url: str,
        html_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extracts full 51-feature vector for a single URL and optional HTML text.
        """
        url_dict = url_feature_extractor.extract_dict(url)
        reg_domain = domain_parser.parse(url).registered_domain

        if html_content:
            web_dict = webpage_feature_extractor.extract_from_html(
                html_content=html_content,
                base_url=url,
                registered_domain=reg_domain
            )
        else:
            web_dict = webpage_feature_extractor.get_default_missing_features()

        combined = {**url_dict, **web_dict}
        feature_vector = [float(combined.get(f, 0.0)) for f in self.feature_names]
        
        return {
            "feature_dict": combined,
            "feature_vector": feature_vector,
            "feature_names": self.feature_names
        }

    def transform_dataset(
        self,
        df: pd.DataFrame,
        url_col: str = "url",
        html_col: Optional[str] = "html_text"
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Transforms a dataframe of URLs into a numpy feature matrix.
        """
        records = []
        has_html = html_col and html_col in df.columns

        for _, row in df.iterrows():
            url = str(row[url_col])
            html = str(row[html_col]) if (has_html and pd.notna(row[html_col])) else None
            extracted = self.extract_features_single(url, html)
            records.append(extracted["feature_vector"])

        return np.array(records, dtype=np.float32), self.feature_names

pipeline = PhishGuardPipeline()

