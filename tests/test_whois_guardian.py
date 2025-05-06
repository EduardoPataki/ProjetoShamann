# tests/test_whois_guardian.py

from shamann.modules.whois_guardian import perform_whois_lookup

def test_perform_whois_lookup():
    result = perform_whois_lookup("example.com")
    assert "domain" in result.lower() or "name" in result.lower()
