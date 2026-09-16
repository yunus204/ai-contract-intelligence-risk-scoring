from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.contracts import (
    router as contracts_router,
)
from backend.app.api.search import (
    router as search_router,
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