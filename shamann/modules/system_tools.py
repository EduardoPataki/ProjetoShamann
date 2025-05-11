import subprocess
import os
import shutil
import time

class SystemTools:

    @staticmethod
    def clean_temp_files():
        try:
            shutil.rmtree('/tmp/', ignore_errors=True)
            os.makedirs('/tmp/', exist_ok=True)
            return {"task": "clean_temp", "result": "success"}
        except Exception as e:
            return {"task": "clean_temp", "result": "error", "message": str(e)}

    @staticmethod
    def verify_disk_usage():
        try:
            result = subprocess.run(["df", "-h"], capture_output=True, text=True)
            return {"task": "disk_usage", "result": "success", "output": result.stdout.strip()}
        except Exception as e:
            return {"task": "disk_usage", "result": "error", "message": str(e)}

    @staticmethod
    def sync_time():
        try:
            subprocess.run(["ntpdate", "-u", "pool.ntp.org"], capture_output=True)
            return {"task": "sync_time", "result": "success"}
        except Exception as e:
            return {"task": "sync_time", "result": "error", "message": str(e)}

    @staticmethod
    def check_dependencies():
        tools = ["nmap", "dig", "whois"]
        missing = [tool for tool in tools if shutil.which(tool) is None]
        if missing:
            return {"task": "check_dependencies", "result": "warning", "missing": missing}
        return {"task": "check_dependencies", "result": "success"}

    @staticmethod
    def create_backup():
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = f"/tmp/shamann_backup_{timestamp}.tar.gz"
            subprocess.run(["tar", "-czf", backup_file, "--exclude=/proc", "--exclude=/sys", "/etc", "/home"], check=True)
            return {"task": "backup", "result": "success", "backup_file": backup_file}
        except Exception as e:
            return {"task": "backup", "result": "error", "message": str(e)}

    @staticmethod
    def activate_firewall():
        try:
            subprocess.run(["ufw", "enable"], check=True)
            return {"task": "firewall", "result": "success"}
        except Exception as e:
            return {"task": "firewall", "result": "error", "message": str(e)}

    @staticmethod
    def start_network_monitor():
        try:
            subprocess.Popen(["iftop", "-t"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"task": "network_monitor", "result": "started"}
        except Exception as e:
            return {"task": "network_monitor", "result": "error", "message": str(e)}

    @staticmethod
    def launch_honeypot():
        try:
            # Suporte básico com cowrie ou dummy listener
            return {"task": "honeypot", "result": "placeholder: configure honeypot manually"}
        except Exception as e:
            return {"task": "honeypot", "result": "error", "message": str(e)}
