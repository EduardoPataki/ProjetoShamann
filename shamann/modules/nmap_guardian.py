import subprocess

class NmapGuardian:
    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        try:
            cmd = ["nmap"] + options.split() + [target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {
                "target": target,
                "command": " ".join(cmd),
                "output": result.stdout,
                "status": "success" if result.returncode == 0 else "warning"
            }
        except Exception as e:
            return {
                "target": target,
                "status": "error",
                "error_message": str(e)
            }
