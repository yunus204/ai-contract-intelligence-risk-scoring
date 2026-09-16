from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.contracts import (
    router as contracts_router,
)
from backend.app.api.search import (
    router as search_router,
)
import logging
import time
import uuid

from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import (
    JSONResponse,
)

from backend.app.utils.logging_config import (
    setup_logging,
)
setup_logging()

logger = logging.getLogger(
    "contract_intelligence.api"
)
app = FastAPI(
    title="AI Contract Intelligence API",
    description=(
        "AI-powered legal contract analysis, "
        "entity extraction, clause detection, "
        "risk scoring and semantic search."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(
        uuid.uuid4()
    )

    start_time = (
        time.perf_counter()
    )

    try:
        response = await call_next(
            request
        )

        duration_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2,
        )

        logger.info(
            "HTTP request completed",
            extra={
                "request_id":
                    request_id,

                "method":
                    request.method,

                "path":
                    request.url.path,

                "status_code":
                    response.status_code,

                "duration_ms":
                    duration_ms,
            },
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    except Exception:
        duration_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2,
        )

        logger.exception(
            "Unhandled request error",
            extra={
                "request_id":
                    request_id,

                "method":
                    request.method,

                "path":
                    request.url.path,

                "status_code":
                    500,

                "duration_ms":
                    duration_ms,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "error":
                    "Internal server error",

                "request_id":
                    request_id,
            },
            headers={
                "X-Request-ID":
                    request_id,
            },
        )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    contracts_router
)
app.include_router(
    search_router
)

@app.get("/")
def root():
    return {
        "service":
            "AI Contract Intelligence API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Request validation failed",
        extra={
            "method":
                request.method,

            "path":
                request.url.path,

            "status_code":
                422,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "error":
                "Validation error",

            "details":
                exc.errors(),
        },
    )