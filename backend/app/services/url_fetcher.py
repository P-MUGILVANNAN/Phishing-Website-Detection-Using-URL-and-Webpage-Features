import io
import urllib.parse
from typing import NamedTuple, Optional, Dict
import httpx
from app.config import settings
from app.core.security import resolve_and_validate_host

class FetchResult(NamedTuple):
    is_success: bool
    status_code: Optional[int]
    html_content: Optional[str]
    final_url: Optional[str]
    redirects_count: int
    content_type: Optional[str]
    error_message: Optional[str]

class SafeURLFetcher:
    def __init__(
        self,
        timeout: float = settings.SAFE_FETCH_TIMEOUT_SECONDS,
        max_bytes: int = settings.SAFE_FETCH_MAX_BYTES,
        max_redirects: int = settings.SAFE_FETCH_MAX_REDIRECTS,
    ):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects

    def fetch(self, url: str) -> FetchResult:
        if not settings.ENABLE_WEBPAGE_FETCH:
            return FetchResult(
                is_success=False,
                status_code=None,
                html_content=None,
                final_url=url,
                redirects_count=0,
                content_type=None,
                error_message="Safe webpage fetching is disabled by default in server configuration."
            )

        current_url = url
        redirects_count = 0

        # Custom redirect loop with revalidation at every hop
        for _ in range(self.max_redirects + 1):
            parsed = urllib.parse.urlsplit(current_url)
            scheme = parsed.scheme.lower()
            if scheme not in {"http", "https"}:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message=f"SSRF Protection: Forbidden scheme '{scheme}'. Only HTTP and HTTPS allowed."
                )

            hostname = parsed.hostname
            if not hostname:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message="SSRF Protection: Missing or malformed hostname."
                )

            # Pre-connect DNS and IP security validation
            is_safe, resolved_ips, error_msg = resolve_and_validate_host(hostname)
            if not is_safe:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message=f"SSRF Protection blocked connection: {error_msg}"
                )

            # Perform controlled HTTP request with streaming to enforce byte limit
            headers = {
                "User-Agent": "PhishGuard-SafeFetcher/1.0 (+https://github.com/phishguard-ai; security scanner)",
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
                "Accept-Encoding": "identity",
            }

            try:
                with httpx.Client(
                    follow_redirects=False,
                    timeout=httpx.Timeout(self.timeout, connect=min(3.0, self.timeout)),
                    verify=True,
                ) as client:
                    with client.stream("GET", current_url, headers=headers) as response:
                        # Check redirects
                        if response.status_code in (301, 302, 303, 307, 308):
                            location = response.headers.get("Location")
                            if not location:
                                return FetchResult(
                                    is_success=False,
                                    status_code=response.status_code,
                                    html_content=None,
                                    final_url=current_url,
                                    redirects_count=redirects_count,
                                    content_type=response.headers.get("Content-Type"),
                                    error_message="Redirect response missing Location header."
                                )
                            # Join relative redirect
                            current_url = urllib.parse.urljoin(current_url, location)
                            redirects_count += 1
                            if redirects_count > self.max_redirects:
                                return FetchResult(
                                    is_success=False,
                                    status_code=response.status_code,
                                    html_content=None,
                                    final_url=current_url,
                                    redirects_count=redirects_count,
                                    content_type=None,
                                    error_message=f"SSRF Protection: Max redirects limit ({self.max_redirects}) exceeded."
                                )
                            continue

                        # Check content type
                        content_type = response.headers.get("Content-Type", "").lower()
                        if not any(t in content_type for t in ["text/html", "application/xhtml+xml", "text/plain"]):
                            return FetchResult(
                                is_success=False,
                                status_code=response.status_code,
                                html_content=None,
                                final_url=current_url,
                                redirects_count=redirects_count,
                                content_type=content_type,
                                error_message=f"Rejected content type: '{content_type}'. Expected HTML."
                            )

                        # Read bounded bytes
                        buffer = io.BytesIO()
                        bytes_read = 0
                        for chunk in response.iter_bytes(chunk_size=8192):
                            bytes_read += len(chunk)
                            if bytes_read > self.max_bytes:
                                return FetchResult(
                                    is_success=False,
                                    status_code=response.status_code,
                                    html_content=None,
                                    final_url=current_url,
                                    redirects_count=redirects_count,
                                    content_type=content_type,
                                    error_message=f"Response exceeded size threshold of {self.max_bytes} bytes."
                                )
                            buffer.write(chunk)

                        html_text = buffer.getvalue().decode("utf-8", errors="replace")
                        return FetchResult(
                            is_success=True,
                            status_code=response.status_code,
                            html_content=html_text,
                            final_url=current_url,
                            redirects_count=redirects_count,
                            content_type=content_type,
                            error_message=None
                        )

            except httpx.ConnectError as e:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message=f"Connection failed: {str(e)}"
                )
            except httpx.TimeoutException:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message="Connection timed out."
                )
            except Exception as e:
                return FetchResult(
                    is_success=False,
                    status_code=None,
                    html_content=None,
                    final_url=current_url,
                    redirects_count=redirects_count,
                    content_type=None,
                    error_message=f"Controlled retrieval error: {str(e)}"
                )

        return FetchResult(
            is_success=False,
            status_code=None,
            html_content=None,
            final_url=current_url,
            redirects_count=redirects_count,
            content_type=None,
            error_message="Redirect limit reached."
        )

safe_fetcher = SafeURLFetcher()

