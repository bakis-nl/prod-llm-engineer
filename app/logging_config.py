import json
import logging
import sys
from datetime import datetime, timezone

from .request_context import get_request_id


class JSONFormatter(logging.Formatter):
    
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            #"request_id": get_request_id(),
        }

        for field in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "model",
        ):
            if hasattr(record, field):
                data[field] = getattr(record, field)

        return json.dumps(data)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("app")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    