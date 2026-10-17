import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from src.api.constants import (
    INTERNAL_ERROR,
    INVALID_QUESTION_ERROR,
    MODEL_CALL_ERROR,
    MODEL_LOGIN_ERROR,
    USAGE_LIMIT_ERROR,
)
from src.api.schemas.ask_request import AskRequest
from src.api.schemas.error_response import ErrorResponse
from src.api.schemas.health_status import HealthStatus
from src.llm.cli_client import CliError, LoginCheckFailed, UsageGuardTriggered
from src.pipeline.schemas.answer import Answer
from src.pipeline.service import answer_question, load_default_system

logger = logging.getLogger(__name__)


@asynccontextmanager
async def load_models_on_startup(app: FastAPI):
    load_default_system()
    yield


app = FastAPI(lifespan=load_models_on_startup)


def build_error_response(status_code: int, error_code: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(error=error_code).model_dump())


@app.exception_handler(UsageGuardTriggered)
def handle_usage_limit(request: Request, error: UsageGuardTriggered) -> JSONResponse:
    logger.warning("Usage guard stopped the model call: %s", error)
    return build_error_response(status.HTTP_503_SERVICE_UNAVAILABLE, USAGE_LIMIT_ERROR)


@app.exception_handler(LoginCheckFailed)
def handle_login_failure(request: Request, error: LoginCheckFailed) -> JSONResponse:
    logger.error("Model login check failed: %s", error)
    return build_error_response(status.HTTP_503_SERVICE_UNAVAILABLE, MODEL_LOGIN_ERROR)


@app.exception_handler(CliError)
def handle_model_call_failure(request: Request, error: CliError) -> JSONResponse:
    logger.error("Model call failed: %s", error)
    return build_error_response(status.HTTP_502_BAD_GATEWAY, MODEL_CALL_ERROR)


@app.exception_handler(RequestValidationError)
def handle_invalid_question(request: Request, error: RequestValidationError) -> JSONResponse:
    return build_error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, INVALID_QUESTION_ERROR)


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    return build_error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, INTERNAL_ERROR)


@app.get("/health")
def check_health() -> HealthStatus:
    return HealthStatus(ready=True)


@app.post("/ask")
def ask(ask_request: AskRequest) -> Answer:
    return answer_question(ask_request.question)


app.mount("/", StaticFiles(directory=config.WEB_DIR, html=True, check_dir=False))
