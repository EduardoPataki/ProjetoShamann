# tests/test_mestre.py

import unittest
from shamann.main import Mestre

class TestMestre(unittest.TestCase):

    def test_execute_scan_whois(self):
        # Domínio de exemplo bem conhecido (responde WHOIS corretamente)
        result = Mestre.execute_scan("whois", "example.com")

        # Verificações básicas
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("whois_data", result)

    def test_execute_scan_invalid_guardian(self):
        # Guardião que não existe
        result = Mestre.execute_scan("fantasma", "example.com")

        self.assertEqual(result["status"], "error")
        self.assertIn("error_message", result)
        self.assertIn("não encontrado", result["error_message"])

if __name__ == '__main__':
    unittest.main()
