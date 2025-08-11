"""
Logging configuration for the NLP translation application.
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage'
            }:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


class TranslationLogger:
    """Specialized logger for translation operations."""
    
    def __init__(self, name: str = "translation"):
        self.logger = logging.getLogger(name)
    
    def log_translation_request(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
        model: str,
        user_id: str = None
    ):
        """Log translation request."""
        self.logger.info(
            "Translation request received",
            extra={
                "event_type": "translation_request",
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model": model,
                "text_length": len(source_text),
                "user_id": user_id
            }
        )
    
    def log_translation_response(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        model: str,
        confidence: float,
        processing_time: float,
        user_id: str = None
    ):
        """Log translation response."""
        self.logger.info(
            "Translation completed",
            extra={
                "event_type": "translation_response",
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model": model,
                "text_length": len(source_text),
                "translated_length": len(translated_text),
                "confidence": confidence,
                "processing_time_ms": processing_time * 1000,
                "user_id": user_id
            }
        )
    
    def log_translation_error(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
        model: str,
        error: str,
        user_id: str = None
    ):
        """Log translation error."""
        self.logger.error(
            "Translation failed",
            extra={
                "event_type": "translation_error",
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model": model,
                "text_length": len(source_text),
                "error": error,
                "user_id": user_id
            }
        )
    
    def log_cache_hit(self, cache_key: str, source_lang: str, target_lang: str):
        """Log cache hit."""
        self.logger.debug(
            "Cache hit",
            extra={
                "event_type": "cache_hit",
                "cache_key": cache_key,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )
    
    def log_cache_miss(self, cache_key: str, source_lang: str, target_lang: str):
        """Log cache miss."""
        self.logger.debug(
            "Cache miss",
            extra={
                "event_type": "cache_miss",
                "cache_key": cache_key,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        )


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    structured_logging: bool = True,
    console_logging: bool = True
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        structured_logging: Whether to use structured JSON logging
        console_logging: Whether to enable console logging
    """
    # Create logs directory if log file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure handlers
    handlers = []
    
    if console_logging:
        if structured_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        handlers.append(console_handler)
    
    if log_file:
        if structured_logging:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # Create main application logger
    logger = logging.getLogger("nlp_translation")
    logger.info(
        "Logging initialized",
        extra={
            "log_level": log_level,
            "structured_logging": structured_logging,
            "console_logging": console_logging,
            "log_file": log_file
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


def get_translation_logger() -> TranslationLogger:
    """Get the specialized translation logger."""
    return TranslationLogger()


# Default logging configuration for development
DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "structured": {
            "()": StructuredFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "structured",
            "filename": "logs/app.log",
            "mode": "a"
        }
    },
    "loggers": {
        "nlp_translation": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "translation": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}


def configure_development_logging():
    """Configure logging for development environment."""
    setup_logging(
        log_level="DEBUG",
        log_file="logs/app.log",
        structured_logging=True,
        console_logging=True
    )


def configure_production_logging():
    """Configure logging for production environment."""
    setup_logging(
        log_level="INFO",
        log_file="logs/app.log",
        structured_logging=True,
        console_logging=False
    )


def configure_testing_logging():
    """Configure logging for testing environment."""
    setup_logging(
        log_level="WARNING",
        structured_logging=False,
        console_logging=True
    )


# Performance monitoring logger
class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: str = None
    ):
        """Log API request performance."""
        self.logger.info(
            "API request completed",
            extra={
                "event_type": "api_request",
                "endpoint": endpoint,
                "method": method,
                "response_time_ms": response_time * 1000,
                "status_code": status_code,
                "user_id": user_id
            }
        )
    
    def log_database_query(
        self,
        query_type: str,
        execution_time: float,
        rows_affected: int = None
    ):
        """Log database query performance."""
        self.logger.debug(
            "Database query executed",
            extra={
                "event_type": "database_query",
                "query_type": query_type,
                "execution_time_ms": execution_time * 1000,
                "rows_affected": rows_affected
            }
        )
    
    def log_translation_batch(
        self,
        batch_size: int,
        total_time: float,
        avg_time_per_item: float
    ):
        """Log batch translation performance."""
        self.logger.info(
            "Batch translation completed",
            extra={
                "event_type": "batch_translation",
                "batch_size": batch_size,
                "total_time_ms": total_time * 1000,
                "avg_time_per_item_ms": avg_time_per_item * 1000
            }
        )
