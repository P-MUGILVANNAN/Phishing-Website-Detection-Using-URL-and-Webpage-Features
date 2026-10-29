import math
import re
import urllib.parse
from typing import Dict, Any, List
import pandas as pd

from app.services.url_normalizer import URLNormalizer, NormalizedURL
from app.services.domain_parser import domain_parser

SUSPICIOUS_KEYWORDS = {
    "login", "verify", "secure", "account", "update", "banking", "service",
    "signin", "admin", "confirm", "security", "support", "auth", "wallet",
    "recover", "portal", "billing", "protect", "authenticate", "checkpoint",
    "validation", "password", "credential", "suspend", "free", "bonus"
}

POPULAR_BRANDS = {
    "paypal", "google", "apple", "microsoft", "amazon", "netflix",
    "facebook", "instagram", "yahoo", "chase", "wellsfargo", "bankofamerica",
    "citibank", "dropbox", "adobe", "ebay", "walmart", "steam", "binance",
    "coinbase", "metamask", "whatsapp", "telegram", "icloud", "outlook"
}

IP_PATTERN = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")

def calculate_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq: Dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    length = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)

class URLFeatureExtractor:
    VERSION = "1.0.0"

    FEATURE_NAMES: List[str] = [
        "url_length",
        "hostname_length",
        "registered_domain_length",
        "path_length",
        "query_length",
        "count_dots",
        "count_hyphens",
        "count_underscores",
        "count_slashes",
        "count_question_marks",
        "count_equals",
        "count_ampersands",
        "count_percent",
        "count_digits",
        "digit_ratio",
        "subdomain_depth",
        "num_parameters",
        "num_path_segments",
        "suspicious_punctuation_count",
        "has_ip_hostname",
        "has_at_symbol",
        "has_nonstandard_port",
        "has_fragment",
        "is_https",
        "is_punycode",
        "has_encoded_chars",
        "has_suspicious_words_hostname",
        "suspicious_words_count",
        "has_brand_in_subdomain",
        "brand_in_subdomain_count",
        "hostname_entropy",
        "path_entropy"
    ]

    def __init__(self):
        self.normalizer = URLNormalizer()
        self.parser = domain_parser

    def extract_dict(self, raw_url: str) -> Dict[str, Any]:
        norm: NormalizedURL = self.normalizer.normalize(raw_url)
        full_url = norm.normalized_url or raw_url or ""
        hostname = norm.hostname or ""
        path = norm.path or ""
        query = norm.query or ""
        fragment = norm.fragment or ""
        
        parsed_dom = self.parser.parse(hostname)
        reg_domain = parsed_dom.registered_domain
        subdomain = parsed_dom.subdomain

        url_length = len(full_url)
        hostname_length = len(hostname)
        registered_domain_length = len(reg_domain)
        path_length = len(path)
        query_length = len(query)

        count_dots = full_url.count(".")
        count_hyphens = full_url.count("-")
        count_underscores = full_url.count("_")
        count_slashes = full_url.count("/")
        count_question_marks = full_url.count("?")
        count_equals = full_url.count("=")
        count_ampersands = full_url.count("&")
        count_percent = full_url.count("%")
        count_digits = sum(c.isdigit() for c in full_url)
        digit_ratio = round(count_digits / max(url_length, 1), 4)

        # Subdomain depth
        if subdomain:
            subdomain_depth = len(subdomain.split("."))
        else:
            subdomain_depth = 0

        # Number of parameters
        num_parameters = len(urllib.parse.parse_qs(query)) if query else 0

        # Path segments
        path_segments = [seg for seg in path.split("/") if seg]
        num_path_segments = len(path_segments)

        # Suspicious punctuation combinations
        suspicious_punct = ["//", "..", "--", "@@", "-.-", "%20", "%00"]
        suspicious_punctuation_count = sum(full_url.count(p) for p in suspicious_punct)
        # remove normal http:// or https:// slash count
        if norm.scheme:
            suspicious_punctuation_count = max(0, suspicious_punctuation_count - 1)

        # Hostname IP check
        has_ip_hostname = 1 if IP_PATTERN.match(hostname) else 0

        # At symbol in URL
        has_at_symbol = 1 if "@" in full_url else 0

        # Nonstandard port
        has_nonstandard_port = 0
        if norm.port is not None:
            if (norm.scheme == "http" and norm.port != 80) or (norm.scheme == "https" and norm.port != 443):
                has_nonstandard_port = 1

        # Fragment
        has_fragment = 1 if bool(fragment) else 0

        # HTTPS
        is_https = 1 if norm.scheme == "https" else 0

        # Punycode / IDN
        is_punycode = 1 if "xn--" in hostname else 0

        # Encoded chars
        has_encoded_chars = 1 if count_percent > 0 else 0

        # Suspicious words in hostname & path
        host_parts = re.split(r"[-._]", hostname.lower())
        suspicious_words_found = [w for w in host_parts if w in SUSPICIOUS_KEYWORDS]
        suspicious_words_count = len(suspicious_words_found)
        has_suspicious_words_hostname = 1 if suspicious_words_count > 0 else 0

        # Brand names in subdomain
        subdomain_tokens = re.split(r"[-._]", subdomain.lower())
        brands_found = [b for b in subdomain_tokens if b in POPULAR_BRANDS]
        brand_in_subdomain_count = len(brands_found)
        has_brand_in_subdomain = 1 if brand_in_subdomain_count > 0 else 0

        # Entropies
        hostname_entropy = calculate_entropy(hostname)
        path_entropy = calculate_entropy(path)

        return {
            "url_length": url_length,
            "hostname_length": hostname_length,
            "registered_domain_length": registered_domain_length,
            "path_length": path_length,
            "query_length": query_length,
            "count_dots": count_dots,
            "count_hyphens": count_hyphens,
            "count_underscores": count_underscores,
            "count_slashes": count_slashes,
            "count_question_marks": count_question_marks,
            "count_equals": count_equals,
            "count_ampersands": count_ampersands,
            "count_percent": count_percent,
            "count_digits": count_digits,
            "digit_ratio": digit_ratio,
            "subdomain_depth": subdomain_depth,
            "num_parameters": num_parameters,
            "num_path_segments": num_path_segments,
            "suspicious_punctuation_count": suspicious_punctuation_count,
            "has_ip_hostname": has_ip_hostname,
            "has_at_symbol": has_at_symbol,
            "has_nonstandard_port": has_nonstandard_port,
            "has_fragment": has_fragment,
            "is_https": is_https,
            "is_punycode": is_punycode,
            "has_encoded_chars": has_encoded_chars,
            "has_suspicious_words_hostname": has_suspicious_words_hostname,
            "suspicious_words_count": suspicious_words_count,
            "has_brand_in_subdomain": has_brand_in_subdomain,
            "brand_in_subdomain_count": brand_in_subdomain_count,
            "hostname_entropy": hostname_entropy,
            "path_entropy": path_entropy
        }

    def extract_features(self, raw_url: str) -> List[float]:
        feat_dict = self.extract_dict(raw_url)
        return [float(feat_dict[k]) for k in self.FEATURE_NAMES]

    def extract_dataframe(self, urls: List[str]) -> pd.DataFrame:
        data = [self.extract_dict(u) for u in urls]
        return pd.DataFrame(data, columns=self.FEATURE_NAMES)

url_feature_extractor = URLFeatureExtractor()

