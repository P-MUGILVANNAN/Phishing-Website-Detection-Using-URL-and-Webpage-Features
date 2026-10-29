import re
from typing import Dict, Any, List
from app.services.url_features import POPULAR_BRANDS

LOGIN_KEYWORDS = ["login", "sign in", "signin", "log in", "username", "password", "user id", "passcode", "access code"]
VERIFY_KEYWORDS = ["verify", "verification", "confirm", "identity", "validation", "suspended", "security update", "unauthorized"]
PASSWORD_RESET_KEYWORDS = ["reset password", "forgot password", "change password", "new password", "recovery phrase"]
FINANCIAL_KEYWORDS = ["bank", "credit card", "debit card", "cvv", "billing", "invoice", "payment", "wallet", "ssn", "wire transfer"]
URGENCY_KEYWORDS = ["urgent", "immediately", "within 24 hours", "account suspended", "locked", "action required", "terminate", "limited time"]

class TextProcessor:
    @staticmethod
    def clean_text(raw_text: str) -> str:
        if not raw_text:
            return ""
        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", raw_text).strip()
        return cleaned

    @classmethod
    def extract_text_risk_indicators(
        cls,
        page_text: str,
        page_title: str,
        registered_domain: str
    ) -> Dict[str, Any]:
        combined_text = f"{page_title} {page_text}".lower()
        
        login_matches = sum(combined_text.count(kw) for kw in LOGIN_KEYWORDS)
        verify_matches = sum(combined_text.count(kw) for kw in VERIFY_KEYWORDS)
        pw_reset_matches = sum(combined_text.count(kw) for kw in PASSWORD_RESET_KEYWORDS)
        financial_matches = sum(combined_text.count(kw) for kw in FINANCIAL_KEYWORDS)
        urgency_matches = sum(combined_text.count(kw) for kw in URGENCY_KEYWORDS)

        # Brand impersonation check
        # Look for brand mentions in title/text when registered domain does NOT contain the brand name
        brands_mentioned = [b for b in POPULAR_BRANDS if b in combined_text]
        impersonated_brands = [b for b in brands_mentioned if b not in registered_domain.lower()]
        brand_impersonation_count = len(impersonated_brands)

        # Title-to-domain mismatch:
        # If title mentions a well-known brand or financial entity not reflected in domain
        title_domain_mismatch = 1 if (brand_impersonation_count > 0 and any(b in page_title.lower() for b in impersonated_brands)) else 0

        return {
            "login_keyword_freq": login_matches,
            "verify_keyword_freq": verify_matches,
            "pw_reset_keyword_freq": pw_reset_matches,
            "financial_keyword_freq": financial_matches,
            "urgency_keyword_freq": urgency_matches,
            "brand_impersonation_count": brand_impersonation_count,
            "title_domain_mismatch": title_domain_mismatch,
            "impersonated_brands": impersonated_brands
        }

text_processor = TextProcessor()

