import urllib.parse
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from app.services.domain_parser import domain_parser
from app.services.text_processor import text_processor

class WebpageFeatureExtractor:
    FEATURE_NAMES: List[str] = [
        "page_features_available",
        "title_length",
        "text_length",
        "num_forms",
        "num_password_inputs",
        "num_external_links",
        "num_internal_links",
        "num_iframes",
        "num_scripts",
        "has_login_form",
        "num_hidden_inputs",
        "external_resource_ratio",
        "has_external_form_action",
        "login_keyword_freq",
        "verify_keyword_freq",
        "pw_reset_keyword_freq",
        "financial_keyword_freq",
        "urgency_keyword_freq",
        "brand_impersonation_count",
        "title_domain_mismatch"
    ]

    @classmethod
    def get_default_missing_features(cls) -> Dict[str, Any]:
        result = {feat: 0 for feat in cls.FEATURE_NAMES}
        result["page_features_available"] = 0
        result["page_title"] = ""
        result["extracted_text"] = ""
        result["impersonated_brands"] = []
        return result

    @classmethod
    def extract_from_html(
        cls,
        html_content: str,
        base_url: str,
        registered_domain: str
    ) -> Dict[str, Any]:
        if not html_content or not isinstance(html_content, str):
            return cls.get_default_missing_features()

        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return cls.get_default_missing_features()

        # Remove script and style elements for clean text extraction
        for element in soup(["script", "style", "noscript", "svg"]):
            element.extract()

        title_tag = soup.find("title")
        page_title = title_tag.get_text().strip() if title_tag else ""
        raw_text = soup.get_text(separator=" ", strip=True)
        cleaned_text = text_processor.clean_text(raw_text)

        title_length = len(page_title)
        text_length = len(cleaned_text)

        # Forms analysis
        forms = soup.find_all("form")
        num_forms = len(forms)
        password_inputs = soup.find_all("input", {"type": "password"})
        num_password_inputs = len(password_inputs)
        hidden_inputs = soup.find_all("input", {"type": "hidden"})
        num_hidden_inputs = len(hidden_inputs)

        has_login_form = 1 if (num_password_inputs > 0 or any("login" in str(f).lower() for f in forms)) else 0

        # Check form actions for external domains
        has_external_form_action = 0
        for f in forms:
            action = f.get("action", "")
            if action:
                parsed_action = urllib.parse.urlsplit(action)
                if parsed_action.netloc:
                    action_dom = domain_parser.parse(parsed_action.netloc).registered_domain
                    if action_dom and registered_domain and action_dom.lower() != registered_domain.lower():
                        has_external_form_action = 1
                        break

        # Links analysis
        links = soup.find_all("a", href=True)
        num_internal_links = 0
        num_external_links = 0
        for a in links:
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            parsed_href = urllib.parse.urlsplit(href)
            if not parsed_href.netloc:
                num_internal_links += 1
            else:
                href_dom = domain_parser.parse(parsed_href.netloc).registered_domain
                if href_dom and registered_domain and href_dom.lower() == registered_domain.lower():
                    num_internal_links += 1
                else:
                    num_external_links += 1

        total_links = num_internal_links + num_external_links
        external_resource_ratio = round(num_external_links / max(total_links, 1), 4)

        num_iframes = len(soup.find_all("iframe"))
        num_scripts = len(soup.find_all("script"))

        # NLP text risk indicators
        text_risks = text_processor.extract_text_risk_indicators(
            page_text=cleaned_text,
            page_title=page_title,
            registered_domain=registered_domain
        )

        return {
            "page_features_available": 1,
            "title_length": title_length,
            "text_length": min(text_length, 50000),
            "num_forms": num_forms,
            "num_password_inputs": num_password_inputs,
            "num_external_links": num_external_links,
            "num_internal_links": num_internal_links,
            "num_iframes": num_iframes,
            "num_scripts": num_scripts,
            "has_login_form": has_login_form,
            "num_hidden_inputs": num_hidden_inputs,
            "external_resource_ratio": external_resource_ratio,
            "has_external_form_action": has_external_form_action,
            "login_keyword_freq": text_risks["login_keyword_freq"],
            "verify_keyword_freq": text_risks["verify_keyword_freq"],
            "pw_reset_keyword_freq": text_risks["pw_reset_keyword_freq"],
            "financial_keyword_freq": text_risks["financial_keyword_freq"],
            "urgency_keyword_freq": text_risks["urgency_keyword_freq"],
            "brand_impersonation_count": text_risks["brand_impersonation_count"],
            "title_domain_mismatch": text_risks["title_domain_mismatch"],
            "page_title": page_title[:200],
            "extracted_text": cleaned_text[:1000],
            "impersonated_brands": text_risks["impersonated_brands"]
        }

webpage_feature_extractor = WebpageFeatureExtractor()

