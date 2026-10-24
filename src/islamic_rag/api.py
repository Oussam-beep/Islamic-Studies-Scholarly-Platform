"""FastAPI service exposing the pipeline.

Run with:  uvicorn islamic_rag.api:app --port 8000
The models are loaded lazily on the first /ask request (or call /warmup).
"""
from __future__ import annotations

import os
import threading
from typing import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .config import Settings
from .pipeline import RagPipeline

DISCLAIMER = "For research and reference only; not a religious ruling. Consult qualified scholars."


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)


class SourceModel(BaseModel):
    tag: int
    ref: str
    source_type: str
    text: str
    score: float
    cited: bool


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceModel]
    intents: list[str]
    fallback: bool
    grounded: bool
    disclaimer: str = DISCLAIMER


def create_app(pipeline_factory: Callable[[], RagPipeline] | None = None) -> FastAPI:
    app = FastAPI(
        title="Islamic Studies Scholarly Platform API",
        version=__version__,
        description="Cited question answering over Qur'an, hadith, fiqh and fatwa passages.",
    )
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

    factory = pipeline_factory or (lambda: RagPipeline.from_settings(Settings.from_env()))
    state: dict[str, RagPipeline | None] = {"pipeline": None}
    lock = threading.Lock()

    def get_pipeline() -> RagPipeline:
        with lock:
            if state["pipeline"] is None:
                state["pipeline"] = factory()
            return state["pipeline"]

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "pipeline_loaded": state["pipeline"] is not None}

    @app.post("/warmup")
    def warmup() -> dict:
        get_pipeline()
        return {"status": "loaded"}

    @app.post("/ask", response_model=AskResponse)
    def ask(req: AskRequest) -> AskResponse:
        result = get_pipeline().ask(req.question.strip(), top_k=req.top_k)
        return AskResponse(
            question=result.question,
            answer=result.answer,
            sources=[SourceModel(**s.__dict__) for s in result.sources],
            intents=result.intents,
            fallback=result.fallback,
            grounded=result.grounded,
        )

    return app


app = create_app()
