"""Build (or extend) the Qdrant collection from the raw corpus files.

Example::

    python -m islamic_rag.build_index --data-dir data/raw                # quran + hadith + fiqh + fatwa
    python -m islamic_rag.build_index --limit 200 --recreate             # quick trial run
    python -m islamic_rag.build_index --tafsir-books jalalayn al_muyassar
"""
from __future__ import annotations

import argparse
from typing import Callable, Iterable

from qdrant_client import QdrantClient

from .config import Settings
from .corpus import DEFAULT_SOURCES, SOURCE_TYPES, TAFSIR_BOOKS, Passage, iter_corpus
from .embedding import Embedder
from .store import ensure_collection, get_client, upsert


def build_index(
    client: QdrantClient,
    embedder: Embedder,
    passages: Iterable[Passage],
    collection: str,
    batch_size: int = 64,
    recreate: bool = False,
    log: Callable[[str], None] = print,
) -> int:
    """Embed and upsert passages in batches. Idempotent: ids are derived from passage keys."""
    ensure_collection(client, collection, embedder.dim, recreate=recreate)
    batch: list[Passage] = []
    total = 0

    def flush() -> None:
        nonlocal total
        if not batch:
            return
        upsert(client, collection, batch, embedder.embed_documents([p.text for p in batch]))
        total += len(batch)
        batch.clear()
        if (total // batch_size) % 50 == 0:
            log(f"indexed {total:,} passages")

    for p in passages:
        batch.append(p)
        if len(batch) >= batch_size:
            flush()
    flush()
    log(f"done: {total:,} passages upserted into '{collection}'")
    return total


def main() -> None:
    s = Settings.from_env()
    ap = argparse.ArgumentParser(description="Build the Qdrant index from the corpus files.")
    ap.add_argument("--data-dir", default=s.data_dir)
    ap.add_argument("--sources", nargs="+", default=list(DEFAULT_SOURCES), choices=[t for t in SOURCE_TYPES if t != "tafsir"])
    ap.add_argument("--tafsir-books", nargs="*", default=[], choices=sorted(TAFSIR_BOOKS))
    ap.add_argument("--limit", type=int, default=None, help="cap passages per source file (for quick trials)")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--recreate", action="store_true", help="drop and recreate the collection first")
    args = ap.parse_args()

    from .embedding import SentenceTransformerEmbedder

    embedder = SentenceTransformerEmbedder(s.embed_model)
    client = get_client(s)
    passages = iter_corpus(args.data_dir, args.sources, args.tafsir_books, args.limit)
    build_index(client, embedder, passages, s.collection, args.batch_size, args.recreate)


if __name__ == "__main__":
    main()
