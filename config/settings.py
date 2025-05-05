# config/settings.py
import os
import yaml
from pathlib import Path

def load_config(env: str = None) -> dict:
    """Load configuration based on environment."""
    if env is None:
        env = os.getenv("SHAMANN_ENV", "development")
    
    config = {
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/shamann.log",
        },
        "whois": {
            "timeout": 30,
            "retry_count": 3,
        },
        "output_dir": "output",
    }
    
    return config