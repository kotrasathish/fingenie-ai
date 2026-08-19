import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from services.chat_services import chat_service
from schemas.chat import ChatRequest, ChatResponse
from services.database_service import database_service
from logging_config import setup_logging
from fastapi import Request
from fastapi.responses import JSONResponse
from logging_config import setup_logging
from core.exceptions import FinGenieException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from services.chat_services import chat_service

setup_logging()
logger = logging.getLogger("fingenie")
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FinGenie AI",
    description="AI Financial Assistant",
    version="1.0.0"
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],

    allow_credentials=True,

    allow_methods=["GET", "POST", "DELETE"],

    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/chat")
@limiter.limit("20/minute")
async def chat_api(
    request: Request,
    chat_request: ChatRequest
):

    try:

        reply, conversation_id = chat_service.get_reply(
            chat_request.message,
            chat_request.conversation_id
        )

        return {
            "reply": reply,
            "conversation_id": conversation_id
        }

    except Exception as e:

        logger.exception("Chat processing failed")

        return {
            "reply": "Sorry, I'm unable to process your request right now.",
            "conversation_id": chat_request.conversation_id
        }
@app.get("/conversations")
async def get_conversations():
    return database_service.get_conversations()

@app.get("/messages/{conversation_id}")
async def get_messages(conversation_id: int):
    return database_service.get_messages(conversation_id)
@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):

    database_service.delete_conversation(conversation_id)

    return {
        "success": True
    }
@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "FinGenie AI",
        "version": "1.0.0"
    }
@app.get("/ready")
async def ready():

    try:

        from rag.rag_service import rag_service

        rag_service.load_vectorstore()

        return {
            "status": "ready",
            "rag": "ready",
            "ai": "configured"
        }

    except Exception as e:

        return {
            "status": "not_ready",
            "error": str(e)
        }

@app.exception_handler(FinGenieException)
async def fin_genie_exception_handler(
    request: Request,
    exc: FinGenieException
):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    print(
        f"Unhandled error: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error"
        }
    )