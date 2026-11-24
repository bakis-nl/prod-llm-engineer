
import logging
import time
from typing import Dict, Optional
from pydantic import Field

class FakeClient:
    async def complete(self, *, model: str, prompt: str) -> str:
        pass

logger = logging.getLogger("app.llm")

class MockLLMProvider:
    def __init__(self, model: str):
        self.model = model
    
    async def generate(self, prompt: str) -> str:
        start = time.perf_counter()
        logger.info(
            "llm_started",
            extra={"model": self.model},
        )
        try:
            result = f"Mock response to: {prompt}"
            duration_ms = round(
                (time.perf_counter() - start) * 1000, 2
            )
            logger.info(
                "llm_completed",
                extra={
                    "model": self.model,
                    "duration_ms": duration_ms,
                },
            )

            return result
        except Exception:
            logger.exception(
                "llm_failed",
                extra={"model": self.model},
            )
            raise

