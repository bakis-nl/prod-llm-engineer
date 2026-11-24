from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    use_mock: bool | None = None
    model: str | None = None
    client_name: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    model: str | None = None
    client_name: str | None = None
    session_id: str | None = None