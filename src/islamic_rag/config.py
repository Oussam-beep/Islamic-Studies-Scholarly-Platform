"""Runtime settings, overridable through environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    data_dir: str = "data/raw"
    qdrant_path: str = "qdrant_db"          # embedded (local) Qdrant storage
    qdrant_url: str | None = None           # set to use a Qdrant server instead
    qdrant_api_key: str | None = None
    collection: str = "islamic_knowledge_base"
    embed_model: str = "BAAI/bge-m3"
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"
    top_k: int = 5

    @classmethod
    def from_env(cls) -> "Settings":
        d = cls()
        return cls(
            data_dir=os.getenv("ISLAMIC_RAG_DATA_DIR", d.data_dir),
            qdrant_path=os.getenv("QDRANT_PATH", d.qdrant_path),
            qdrant_url=os.getenv("QDRANT_URL") or None,
            qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
            collection=os.getenv("ISLAMIC_RAG_COLLECTION", d.collection),
            embed_model=os.getenv("ISLAMIC_RAG_EMBED_MODEL", d.embed_model),
            llm_model=os.getenv("ISLAMIC_RAG_LLM_MODEL", d.llm_model),
            top_k=int(os.getenv("ISLAMIC_RAG_TOP_K", d.top_k)),
        )
