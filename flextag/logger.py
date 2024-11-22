import logging
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict


class FlexTagLogger:
    """
    Logger for FlexTag with support for both file and console output.
    Handles structured logging for parser states and debug information.
    """

    def __init__(self, log_level: int = logging.DEBUG):
        self.logger = logging.getLogger("flextag")
        self.logger.setLevel(log_level)

        # Create logs directory if it doesn't exist
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Create handlers
        self._setup_file_handlers()
        self._setup_console_handler()

        # Parser state tracking
        self.parser_state: Dict[str, Any] = {
            "current_block": None,
            "current_field": None,
            "position": 0,
            "in_comment": False,
            "errors": [],
        }

    def _setup_file_handlers(self):
        """Set up file handlers for different log levels"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Debug log - contains everything
        debug_handler = logging.FileHandler(self.log_dir / f"debug_{timestamp}.log")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        self.logger.addHandler(debug_handler)

        # Parser state log - structured logging of parser states
        self.state_log_path = self.log_dir / f"parser_state_{timestamp}.jsonl"

        # Error log - only errors and critical issues
        error_handler = logging.FileHandler(self.log_dir / f"error_{timestamp}.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s\nContext: %(context)s\n"
            )
        )
        self.logger.addHandler(error_handler)

    def _setup_console_handler(self):
        """Set up console handler for immediate feedback"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        self.logger.addHandler(console_handler)

    def update_parser_state(self, **kwargs):
        """Update parser state and log it"""
        self.parser_state.update(kwargs)
        self._log_parser_state()

    def _log_parser_state(self):
        """Log current parser state to the state log file"""
        with open(self.state_log_path, "a") as f:
            state_entry = {
                "timestamp": datetime.now().isoformat(),
                "state": self.parser_state.copy(),
            }
            f.write(json.dumps(state_entry) + "\n")

    def _format_extra(self, extra: Dict[str, Any]) -> str:
        """Format extra parameters into a string"""
        if not extra:
            return ""
        return " | " + " | ".join(f"{k}={v}" for k, v in extra.items())

    def debug(self, msg: str, **kwargs):
        """Log debug message with optional context"""
        extra_str = self._format_extra(kwargs)
        self.logger.debug(f"{msg}{extra_str}")

    def info(self, msg: str, **kwargs):
        """Log info message with optional context"""
        extra_str = self._format_extra(kwargs)
        self.logger.info(f"{msg}{extra_str}")

    def warning(self, msg: str, **kwargs):
        """Log warning message with optional context"""
        extra_str = self._format_extra(kwargs)
        self.logger.warning(f"{msg}{extra_str}")

    def error(self, msg: str, **kwargs):
        """Log error message with context"""
        extra_str = self._format_extra(kwargs)
        self.logger.error(f"{msg}{extra_str}", extra={"context": extra_str})
        self.parser_state["errors"].append(
            {"timestamp": datetime.now().isoformat(), "message": msg, "context": kwargs}
        )
        self._log_parser_state()

    def critical(self, msg: str, **kwargs):
        """Log critical message with context"""
        extra_str = self._format_extra(kwargs)
        self.logger.critical(f"{msg}{extra_str}", extra={"context": extra_str})


# Global logger instance
logger = FlexTagLogger()
