import asyncio
from .base import ChatRequest, LLMProvider
from .base import ModelClient

class ModelTimeoutError(Exception):
    """Custom exception to indicate a timeout when calling the model API."""
    pass

class APIProvider:
    def __init__(self, model: str, client: ModelClient, timeout_seconds: float = 30.0):
        self.model = model
        self.client = client
        self.timeout_seconds = timeout_seconds

    async def generate(self, prompt: str) -> str:
        try:
            async with asyncio.timeout(self.timeout_seconds):
                # Await the model API call here.
                # For demonstration purposes, we'll just return the prompt.
                return await self.client.complete(model=self.model, prompt=prompt)
        except TimeoutError as exc:
            raise ModelTimeoutError("Model API timed out") from exc
        
    

