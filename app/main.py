
import asyncio
import json
import logging
from typing import Annotated
from uuid import uuid4
from fastapi import Request,Depends, FastAPI, HTTPException
from time import perf_counter

from .dependencies import get_chat_request, get_llm_provider
from .llm.base import LLMProvider
from .llm.mock import MockLLMProvider
from .schemas import ChatRequest, ChatResponse
from .llm.provider import ModelTimeoutError
from .logging_config import configure_logging
from .middleware import RequestLoggingMiddleware
from .request_context import get_request_id

app = FastAPI(title="Production LLM API")

app.add_middleware(RequestLoggingMiddleware)
logger = logging.getLogger("uvicorn.error")
configure_logging()

'''@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    started_at = perf_counter()

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        json.dumps(
            {
                "event": "http_request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
            }
        )
    )

    return response

'''

@app.get("/health")
async def health():
    return {"status": "ok"}





@app.post("/chat", response_model=ChatResponse)
async def chat(
    #request: ChatRequest,
    request: Annotated[
        ChatRequest, Depends(get_chat_request)
        ],
    provider: Annotated[
        LLMProvider, Depends(get_llm_provider)
        ],
):
    try:
        started_at = perf_counter()
        answer =  await provider.generate(request.message)
    except ModelTimeoutError:
        raise HTTPException(status_code=504, detail="Model API timed out")
    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    

    logger.info(
            json.dumps(
                {
                    "event": "http_request_completed",
                    "request_id": get_request_id(),
                    
                    #"method": request.method,
                    #"path": request.url.path,
                   # "status_code": answer.status_code,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                }
            )
        )
    return ChatResponse(
        response=answer,
        model=request.model,
        session_id=request.session_id 
    )




    

async def run_model_call(chat_request: ChatRequest, generate_fn) -> str:
    started_at = perf_counter()
    result = await generate_fn(chat_request.message)
    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "llm_generate_completed",
                "model": chat_request.model,
                "session_id": chat_request.session_id,
                "duration_ms": duration_ms,
            }
        )
    )
    return result