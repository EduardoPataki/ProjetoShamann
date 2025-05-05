# tests/test_whois_guardian.py
import pytest
from modules.whois_guardian import WhoisGuardian

def test_whois_guardian_initialization():
    guardian = WhoisGuardian()
    assert guardian is not None

def test_whois_lookup():
    guardian = WhoisGuardian()
    # Add your test cases here
    pass

# Add more test cases as needed