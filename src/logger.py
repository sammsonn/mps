"""
Logging utility for the Synapse Strike game.
Provides console and file logging with timestamped log files.
"""

import logging
import os
from datetime import datetime


class GameLogger:
    """Singleton logger that writes to both console and file."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is not None:
            return
        
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create logger
        self._logger = logging.getLogger("SynapseStrike")
        self._logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # File handler with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(logs_dir, f"game_{timestamp}.log")
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
        
        self._logger.info(f"=== Game started - Log file: {log_filename} ===")
    
    def info(self, message):
        """Log an info message."""
        self._logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self._logger.warning(message)
    
    def error(self, message):
        """Log an error message."""
        self._logger.error(message)
    
    def debug(self, message):
        """Log a debug message."""
        self._logger.debug(message)
    
    def game_event(self, event_type, details):
        """Log a game event with structured information."""
        self._logger.info(f"[{event_type}] {details}")
    
    def shutdown(self):
        """Close all handlers and shutdown logger."""
        self._logger.info("=== Game ended ===")
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)


# Global logger instance
logger = GameLogger()
