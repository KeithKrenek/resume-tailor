"""Logging configuration for the Resume Tailor application."""

import logging
import sys
from pathlib import Path
from config.settings import PROJECT_ROOT


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional log file path (defaults to PROJECT_ROOT/logs/app.log)
        console_output: Whether to output logs to console

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger('resume_tailor')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    logger.handlers = []

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
    else:
        log_dir = PROJECT_ROOT / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / 'app.log'

    try:
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    # Ensure main logger is configured
    main_logger = logging.getLogger('resume_tailor')
    if not main_logger.handlers:
        setup_logging()

    return logging.getLogger(f'resume_tailor.{name}')
