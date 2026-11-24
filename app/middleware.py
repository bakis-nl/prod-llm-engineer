
import logging
import re
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .request_context import request_id_var

logger = logging.getLogger("app.http")

VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        incoming_id = request.headers.get("X-Request-ID")

        if incoming_id and VALID_REQUEST_ID.fullmatch(incoming_id):
            request_id = incoming_id
        else:
            request_id = str(uuid.uuid4())

        token = request_id_var.set(request_id)
        start = time.perf_counter()

        logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            },
        )

        try:
            response = await call_next(request)

            duration_ms = round(
                (time.perf_counter() - start) * 1000, 2
            )

            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception:
            logger.exception(
                "request_failed", 
                extra={
                    "request_id": request_id, 
                    "method": request.method, 
                    "path": request.url.path
                },
            )
            raise

        finally:
            request_id_var.reset(token)
