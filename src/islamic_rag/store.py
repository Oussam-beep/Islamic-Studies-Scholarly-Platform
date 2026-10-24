"""Thin Qdrant helpers: client creation, collection setup and point conversion."""
from __future__ import annotations

import warnings
from typing import Sequence

from qdrant_client import QdrantClient, models

from .config import Settings
from .corpus import Passage


def get_client(settings: Settings) -> QdrantClient:
    """Qdrant server if QDRANT_URL is set, otherwise embedded local storage."""
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return QdrantClient(path=settings.qdrant_path)


def ensure_collection(client: QdrantClient, name: str, dim: int, recreate: bool = False) -> None:
    exists = client.collection_exists(name)
    if exists and recreate:
        client.delete_collection(name)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )
    # Payload indexes speed up filtered search on a Qdrant server (no-ops in local mode).
    for field, schema in (
        ("metadata.source_type", models.PayloadSchemaType.KEYWORD),
        ("metadata.ayah_key", models.PayloadSchemaType.KEYWORD),
        ("metadata.ayah_number", models.PayloadSchemaType.INTEGER),
    ):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)  # local mode warns that indexes do nothing
                client.create_payload_index(name, field_name=field, field_schema=schema)
        except Exception:  # already exists / unsupported
            pass


def to_point(passage: Passage, vector: Sequence[float]) -> models.PointStruct:
    return models.PointStruct(
        id=passage.point_id,
        vector=list(vector),
        payload={
            "page_content": passage.text,
            "metadata": {
                "provenance_ref": passage.ref,
                "source_type": passage.source_type,
                **passage.meta,
            },
        },
    )


def upsert(client: QdrantClient, name: str, passages: Sequence[Passage], vectors: Sequence[Sequence[float]]) -> None:
    client.upsert(collection_name=name, points=[to_point(p, v) for p, v in zip(passages, vectors)])
