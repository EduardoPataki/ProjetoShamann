# tests/test_whois_guardian.py
import unittest
from shamann.modules.whois_guardian import WhoisGuardian

class TestWhoisGuardian(unittest.TestCase):

    def test_run_query_success(self):
        result = WhoisGuardian.run_query("example.com")
        self.assertIsInstance(result, str)
        self.assertIn("domain", result.lower())  # ou qualquer campo relevante no retorno

if __name__ == '__main__':
    unittest.main()
