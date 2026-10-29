from typing import NamedTuple, Optional
import tldextract

class ParsedDomain(NamedTuple):
    registered_domain: str
    subdomain: str
    domain_name: str
    suffix: str
    full_hostname: str
    is_valid: bool

class DomainParser:
    def __init__(self, cache_dir: Optional[str] = None):
        # Initialize tldextract with local cache
        self.extractor = tldextract.TLDExtract(
            cache_dir=cache_dir or False
        )

    def parse(self, hostname: str) -> ParsedDomain:
        if not hostname or not isinstance(hostname, str):
            return ParsedDomain(
                registered_domain="",
                subdomain="",
                domain_name="",
                suffix="",
                full_hostname="",
                is_valid=False
            )
            
        clean_host = hostname.strip().lower()
        extracted = self.extractor(clean_host)
        
        # Support newer and legacy tldextract property naming
        registered_domain = getattr(extracted, "top_domain_under_public_suffix", None) or extracted.registered_domain
        # If tldextract failed or it's an IP address
        if not registered_domain:
            registered_domain = clean_host
            
        return ParsedDomain(
            registered_domain=registered_domain,
            subdomain=extracted.subdomain,
            domain_name=extracted.domain,
            suffix=extracted.suffix,
            full_hostname=clean_host,
            is_valid=bool(registered_domain)
        )

domain_parser = DomainParser()
