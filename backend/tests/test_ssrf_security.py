import pytest
from app.core.security import is_ip_prohibited, resolve_and_validate_host
from app.services.url_fetcher import safe_fetcher

def test_loopback_prohibited():
    prohibited, reason = is_ip_prohibited("127.0.0.1")
    assert prohibited is True
    assert "loopback" in reason.lower()

    prohibited6, _ = is_ip_prohibited("::1")
    assert prohibited6 is True

def test_private_rfc1918_prohibited():
    prohibited, _ = is_ip_prohibited("10.0.0.1")
    assert prohibited is True

    prohibited2, _ = is_ip_prohibited("192.168.1.1")
    assert prohibited2 is True

    prohibited3, _ = is_ip_prohibited("172.16.0.5")
    assert prohibited3 is True

def test_cloud_metadata_prohibited():
    prohibited, reason = is_ip_prohibited("169.254.169.254")
    assert prohibited is True
    assert "metadata" in reason.lower() or "prohibited" in reason.lower()

def test_public_ip_allowed():
    prohibited, reason = is_ip_prohibited("8.8.8.8")
    assert prohibited is False
    assert reason == "Allowed"

def test_localhost_hostname_rejected():
    is_safe, _, msg = resolve_and_validate_host("localhost")
    assert is_safe is False
    assert "prohibited" in msg.lower()

def test_safe_fetcher_disabled_by_default():
    # Verify safe fetcher gracefully blocks when disabled
    res = safe_fetcher.fetch("http://127.0.0.1:8000/internal")
    assert res.is_success is False
    assert res.html_content is None

