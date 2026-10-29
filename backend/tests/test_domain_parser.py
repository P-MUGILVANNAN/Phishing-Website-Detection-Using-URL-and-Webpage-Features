import pytest
from app.services.domain_parser import domain_parser

def test_domain_parsing():
    res = domain_parser.parse("mail.google.com")
    assert res.registered_domain == "google.com"
    assert res.subdomain == "mail"
    assert res.suffix == "com"

def test_multi_level_tld():
    res = domain_parser.parse("login.paypal.co.uk")
    assert res.registered_domain == "paypal.co.uk"
    assert res.subdomain == "login"
    assert res.suffix == "co.uk"

def test_ip_address_host():
    res = domain_parser.parse("192.168.1.1")
    assert res.registered_domain == "192.168.1.1"
    assert res.is_valid is True

