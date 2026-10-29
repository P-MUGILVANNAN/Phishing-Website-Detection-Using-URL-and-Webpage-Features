import pytest
from app.services.url_normalizer import URLNormalizer

def test_valid_urls():
    norm = URLNormalizer.normalize("https://google.com/search?q=test")
    assert norm.is_valid is True
    assert norm.scheme == "https"
    assert norm.hostname == "google.com"
    assert norm.path == "/search"
    assert norm.query == "q=test"

def test_missing_scheme():
    norm = URLNormalizer.normalize("example.com/login")
    assert norm.is_valid is True
    assert norm.scheme == "http"
    assert norm.hostname == "example.com"
    assert norm.path == "/login"

def test_unsupported_scheme():
    norm = URLNormalizer.normalize("ftp://ftp.is.co.za/pub/")
    assert norm.is_valid is False
    assert "scheme" in norm.error_message.lower()

def test_default_port_stripping():
    norm = URLNormalizer.normalize("http://example.com:80/path")
    assert norm.is_valid is True
    assert norm.port is None
    assert norm.netloc == "example.com"

def test_nonstandard_port_preserved():
    norm = URLNormalizer.normalize("http://example.com:8080/path")
    assert norm.is_valid is True
    assert norm.port == 8080
    assert norm.netloc == "example.com:8080"

def test_malformed_url():
    norm = URLNormalizer.normalize("")
    assert norm.is_valid is False

