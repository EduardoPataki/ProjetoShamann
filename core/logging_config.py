# core/logging_config.py
import logging
import os
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

# Install rich traceback handler
install(show_locals=True)

def setup_logging(module_name: str) -> logging.Logger:
    """
    Configure logging for pentest operations with rich formatting.
    
    Args:
        module_name: Name of the module requesting the logger
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/pentest_{timestamp}.log"
    
    # Configure logging format
    log_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)
    
    # Rich console handler
    console = Console()
    rich_handler = RichHandler(console=console, rich_tracebacks=True)
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)
    
    return logger
