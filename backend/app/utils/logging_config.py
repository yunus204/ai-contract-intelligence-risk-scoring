import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Format application logs as JSON so they are
    easier to search in Docker, CloudWatch, etc.
    """

    def format(self, record):
        log_record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "level": record.levelname,

            "logger": record.name,

            "message": record.getMessage(),
        }

        optional_fields = [
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "contract_id",
            "task_id",
            "stage",
        ]

        for field in optional_fields:
            value = getattr(
                record,
                field,
                None,
            )

            if value is not None:
                log_record[field] = value

        if record.exc_info:
            log_record[
                "exception"
            ] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_record,
            ensure_ascii=False,
        )


def setup_logging():
    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JsonFormatter()
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(
        log_level
    )

    root_logger.handlers.clear()

    root_logger.addHandler(
        handler
    )

    # Reduce noise from libraries
    logging.getLogger(
        "urllib3"
    ).setLevel(logging.WARNING)

    logging.getLogger(
        "httpx"
    ).setLevel(logging.WARNING)

    logging.getLogger(
        "httpcore"
    ).setLevel(logging.WARNING)