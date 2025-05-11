# shamann/modules/whois_guardian.py
import subprocess
from .base_guardian import BaseGuardian

import whois

class WhoisGuardian:
    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        try:
            whois_data = WhoisGuardian.perform_whois_lookup(target)
            return {
                "target": target,
                "guardian": "whois",
                "status": "success",
                "whois_data": whois_data
            }
        except Exception as e:
            return {
                "target": target,
                "guardian": "whois",
                "status": "error",
                "error_message": str(e)
            }

    @staticmethod
    def perform_whois_lookup(target: str) -> str:
        result = whois.whois(target)
        return str(result)

    @staticmethod
    def run_query(target: str) -> str:
        """Interface direta usada pelos testes unitários"""
        return WhoisGuardian.perform_whois_lookup(target)
