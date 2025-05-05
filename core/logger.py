# core/logger.py
import logging
import sys
from pathlib import Path
from typing import Dict

def setup_logging(config: Dict) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        config (Dict): Logging configuration dictionary
    """
    log_level = config.get('level', 'INFO')
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('file', 'logs/shamann.log')
    
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
