"""
Logging configuration for the AI Interview Assistant.
"""
import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("ai_interview_assistant")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def log_user_interaction(action: str, details: Optional[dict] = None):
    """
    Log user interactions for analytics and debugging.
    
    Args:
        action: The action performed by the user
        details: Additional details about the interaction
    """
    logger = logging.getLogger("ai_interview_assistant")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {}
    }
    
    logger.info(f"User interaction: {log_entry}")

def log_ai_interaction(operation: str, success: bool, details: Optional[dict] = None):
    """
    Log AI service interactions for monitoring and debugging.
    
    Args:
        operation: The AI operation performed
        success: Whether the operation was successful
        details: Additional details about the interaction
    """
    logger = logging.getLogger("ai_interview_assistant")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "success": success,
        "details": details or {}
    }
    
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"AI interaction: {log_entry}")

def log_error(error: Exception, context: str = ""):
    """
    Log errors with context information.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    logger = logging.getLogger("ai_interview_assistant")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context
    }
    
    logger.error(f"Error occurred: {log_entry}", exc_info=True)