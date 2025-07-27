import logging
import sys
from loguru import logger
from pathlib import Path

def setup_logging():
    """
    Configure logging for the application.
    
    This is a minimal version to ensure the application can run.
    """
    # Create logs directory if it doesn't exist
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)
    
    # Remove any existing handlers
    logger.remove()
    
    # Add just a simple console handler
    logger.add(sys.stderr)
    
    # Return configured logger
    return logger 