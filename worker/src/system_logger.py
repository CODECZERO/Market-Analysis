import logging
import os
from datetime import datetime

# Define log directory
LOG_DIR = "/home/codeczero/Desktop/FullStack/Brand-Mention-Reputation-Tracker/market_analysis/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "system_comprehensive.log")

def get_logger(name):
    """
    Get a pre-configured logger that writes to both console and a central file
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # File Handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.INFO)
        file_layout = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_layout)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_layout = logging.Formatter('%(name)s: %(message)s')
        console_handler.setFormatter(console_layout)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

def log_event(component, event_type, details):
    """
    Helper to log structured events
    """
    logger = get_logger("SystemMonitor")
    message = f"[{component}] {event_type}: {details}"
    logger.info(message)
