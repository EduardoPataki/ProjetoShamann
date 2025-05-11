import subprocess
from .base_guardian import BaseGuardian

class DNSGuardian(BaseGuardian):
    @classmethod
    def name(cls) -> str:
        return "dns"

    @classmethod
    def run_scan(cls, target: str, options: str = "") -> dict:
        try:
            options = options.strip()  # Limpa espaços extras
            cmd = ["dig"] + options.split() + [target]  # Monta o comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "target": target,
                "command": " ".join(cmd),
                "output": result.stdout.strip(),
                "status": "success" if result.returncode == 0 else "warning"
            }
        except Exception as e:
            return {
                "target": target,
                "status": "error",
                "error_message": str(e)
            }
