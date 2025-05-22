import os
import subprocess
from datetime import datetime
from .base_guardian import BaseGuardian


class ShamannGuardian(BaseGuardian):
    """
    Guardião Shamann: responsável pela manutenção e defesa do ecossistema do Kali Linux.
    """

    @classmethod
    def name(cls) -> str:
        return "shamann"

    @classmethod
    def run_scan(cls, target: str = "", options: str = "") -> dict:
        """
        Executa uma checagem completa do sistema.
        """
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "check_disk": cls.check_disk_usage(),
                "clear_trash": cls.clear_temp_files(),
                "apt_update": cls.run_apt_update(),
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }

    @staticmethod
    def check_disk_usage() -> str:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        return result.stdout.strip()

    @staticmethod
    def clear_temp_files() -> str:
        try:
            subprocess.run(["rm", "-rf", "/tmp/*", "/var/tmp/*"], check=True)
            return "🧹 Temp folders cleaned."
        except subprocess.CalledProcessError as e:
            return f"Erro ao limpar pastas temporárias: {e}"

    @staticmethod
    def run_apt_update() -> str:
        try:
            subprocess.run(["apt", "update", "-y"], capture_output=True, text=True, check=True)
            subprocess.run(["apt", "upgrade", "-y"], capture_output=True, text=True, check=True)
            return "📦 Sistema atualizado com apt."
        except subprocess.CalledProcessError as e:
            return f"Erro ao atualizar sistema: {e}"

    @staticmethod
    def detect_intrusions() -> str:
        # Placeholder: Integrar com Fail2Ban, auditd ou ferramentas de detecção
        return "🔐 Monitoramento de intrusões ainda não implementado."
