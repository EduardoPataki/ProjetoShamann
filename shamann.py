# shamann.py
import logging
import sys
from pathlib import Path

from config.settings import load_config
from core.logger import setup_logging
from modules.whois_guardian import WhoisGuardian

def main():
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config.get('logging', {}))
    logger = logging.getLogger(__name__)

    try:
        # Initialize WhoisGuardian
        # Teste commiti github
        guardian = WhoisGuardian()

        # Add your main application logic here
        logger.info("Shamann application started")

    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
