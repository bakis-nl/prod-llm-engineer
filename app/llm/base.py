


from typing import Optional, Protocol

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    model: str | None = None
    client_name: str | None = None    
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    model: str
    session_id: str | None = None

class LLMProvider(Protocol):

    async def generate(self, prompt: str) -> str:
        return f"{prompt}"



class ModelClient(Protocol):
    async def complete(self, *, model: str, prompt: str) -> str:
        """Method to call the model API and get a response."""
        pass    