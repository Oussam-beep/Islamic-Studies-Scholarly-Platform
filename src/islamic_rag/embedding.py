"""Embedding interface plus the BAAI/bge-m3 implementation used by the project."""
from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    dim: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    """Multilingual (Arabic/English) dense embeddings, L2-normalised for cosine search.

    Inputs are truncated to `max_seq_length` tokens when embedding. The full passage is
    still stored and shown to the LLM; only the vector is computed from the beginning of
    long passages (mostly long fatwa answers).
    """

    def __init__(
        self,
        model_id: str = "BAAI/bge-m3",
        device: str | None = None,
        max_seq_length: int = 512,
        batch_size: int = 32,
    ) -> None:
        import torch
        from sentence_transformers import SentenceTransformer

        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SentenceTransformer(model_id, device=device)
        self.model.max_seq_length = max_seq_length
        self.batch_size = batch_size
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts, batch_size=self.batch_size, normalize_embeddings=True, show_progress_bar=False
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
