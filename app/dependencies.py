
import os
from typing import Annotated, AsyncIterator

from fastapi import Depends
from .llm.base import ChatRequest, LLMProvider, ModelClient
from .llm.mock import MockLLMProvider ,FakeClient
from .llm.provider import APIProvider
from .llm.client import APIClient
from groq import AsyncGroq


def get_chat_request(request: ChatRequest) -> ChatRequest:
    return request


async def get_llm_provider(
    request: Annotated[ChatRequest, Depends(get_chat_request)],
        
) ->AsyncIterator[LLMProvider]:
    
    if bool(os.getenv("USE_MOCK_LLM", "true").lower() == "true"):
        yield MockLLMProvider( model=request.model or os.getenv("MODEL", "mock"))
        return
    
    model = request.model or os.environ["MODEL"]
    
    async with AsyncGroq(max_retries=0) as sdk:
        yield APIProvider(
            model=model,
            client=APIClient(sdk),
            timeout_seconds=30.0,
        )