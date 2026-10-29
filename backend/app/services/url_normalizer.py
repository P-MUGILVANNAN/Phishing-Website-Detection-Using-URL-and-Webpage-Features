import urllib.parse
from typing import NamedTuple, Optional

class NormalizedURL(NamedTuple):
    original_url: str
    normalized_url: str
    scheme: str
    hostname: str
    netloc: str
    port: Optional[int]
    path: str
    query: str
    fragment: str
    is_valid: bool
    error_message: Optional[str]

class URLNormalizer:
    @staticmethod
    def normalize(raw_url: str) -> NormalizedURL:
        if not raw_url or not isinstance(raw_url, str):
            return NormalizedURL(
                original_url=str(raw_url),
                normalized_url="",
                scheme="",
                hostname="",
                netloc="",
                port=None,
                path="",
                query="",
                fragment="",
                is_valid=False,
                error_message="Empty or non-string URL provided."
            )
        
        stripped_url = raw_url.strip()
        
        # Check scheme
        has_scheme = "://" in stripped_url
        if not has_scheme:
            # Check if scheme is omitted, e.g. "example.com"
            parsing_url = "http://" + stripped_url
        else:
            parsing_url = stripped_url
            
        try:
            parsed = urllib.parse.urlsplit(parsing_url)
        except Exception as e:
            return NormalizedURL(
                original_url=stripped_url,
                normalized_url="",
                scheme="",
                hostname="",
                netloc="",
                port=None,
                path="",
                query="",
                fragment="",
                is_valid=False,
                error_message=f"URL parsing failed: {str(e)}"
            )
            
        scheme = parsed.scheme.lower() if parsed.scheme else "http"
        if scheme not in {"http", "https"}:
            return NormalizedURL(
                original_url=stripped_url,
                normalized_url="",
                scheme=scheme,
                hostname="",
                netloc="",
                port=None,
                path="",
                query="",
                fragment="",
                is_valid=False,
                error_message=f"Unsupported scheme '{scheme}'. Only HTTP and HTTPS are permitted."
            )
            
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return NormalizedURL(
                original_url=stripped_url,
                normalized_url="",
                scheme=scheme,
                hostname="",
                netloc="",
                port=None,
                path="",
                query="",
                fragment="",
                is_valid=False,
                error_message="Missing hostname in URL."
            )
            
        port = parsed.port
        # Reconstruct normalized netloc without default ports
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None
            netloc = hostname
        elif port is not None:
            netloc = f"{hostname}:{port}"
        else:
            netloc = hostname
            
        path = parsed.path
        if not path:
            path = "/"
        elif len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")
            
        normalized_url = urllib.parse.urlunsplit((scheme, netloc, path, parsed.query, parsed.fragment))
        
        return NormalizedURL(
            original_url=stripped_url,
            normalized_url=normalized_url,
            scheme=scheme,
            hostname=hostname,
            netloc=netloc,
            port=port,
            path=path,
            query=parsed.query,
            fragment=parsed.fragment,
            is_valid=True,
            error_message=None
        )

