import os
import subprocess
import shutil
import time
from .base_guardian import BaseGuardian
from ..system_tools import SystemTools  # Arquivo que conterá utilitários auxiliares

class ShamannGuardian(BaseGuardian):
    """
    Guardião Shamann: responsável por manter e proteger o ambiente Kali Linux
    """

    @classmethod
    def name(cls) -> str:
        return "shamann"

    @classmethod
    def run_scan(cls, target: str = "", options: str = "") -> dict:
        """
        Executa rotinas de pré-pentest (manutenção) ou defesa ativa com base nas opções
        Ex: --mode precheck | --mode defend
        """
        result = {"status": "success", "executed_tasks": []}

        mode = options.strip().lower()

        try:
            if mode == "--mode precheck":
                result["executed_tasks"].append(SystemTools.clean_temp_files())
                result["executed_tasks"].append(SystemTools.verify_disk_usage())
                result["executed_tasks"].append(SystemTools.sync_time())
                result["executed_tasks"].append(SystemTools.check_dependencies())
                result["executed_tasks"].append(SystemTools.create_backup())

            elif mode == "--mode defend":
                result["executed_tasks"].append(SystemTools.activate_firewall())
                result["executed_tasks"].append(SystemTools.start_network_monitor())
                result["executed_tasks"].append(SystemTools.launch_honeypot())

            else:
                result["status"] = "error"
                result["error_message"] = "Modo inválido. Use --mode precheck ou --mode defend"

        except Exception as e:
            result["status"] = "error"
            result["error_message"] = str(e)

        return result
