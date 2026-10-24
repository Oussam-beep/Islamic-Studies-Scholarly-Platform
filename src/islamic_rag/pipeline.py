"""End-to-end question answering: route -> retrieve -> generate -> verify citations."""
from __future__ import annotations

from dataclasses import dataclass, field

from qdrant_client import QdrantClient

from .config import Settings
from .embedding import Embedder
from .generate import NO_SOURCES_AR, NO_SOURCES_EN, Generator, build_messages, extract_citations, is_arabic
from .search import search


@dataclass
class SourceOut:
    tag: int            # the number used in the answer: [Source <tag>]
    ref: str
    source_type: str
    text: str
    score: float
    cited: bool         # the answer actually cites this source


@dataclass
class Answer:
    question: str
    answer: str
    sources: list[SourceOut] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    fallback: bool = False   # intent filter matched nothing; sources come from an unfiltered search
    grounded: bool = False   # the answer cites at least one retrieved source


class RagPipeline:
    def __init__(self, client: QdrantClient, embedder: Embedder, generator: Generator, collection: str, top_k: int = 5):
        self.client, self.embedder, self.generator = client, embedder, generator
        self.collection, self.top_k = collection, top_k

    def ask(self, question: str, top_k: int | None = None) -> Answer:
        result = search(self.client, self.embedder, question, self.collection, limit=top_k or self.top_k)
        if not result.hits:
            msg = NO_SOURCES_AR if is_arabic(question) else NO_SOURCES_EN
            return Answer(question=question, answer=msg, intents=result.intents)

        text = self.generator.generate(build_messages(question, result.hits))
        cited = set(extract_citations(text, len(result.hits)))
        sources = [
            SourceOut(i, h.ref, h.source_type, h.text, h.score, cited=i in cited)
            for i, h in enumerate(result.hits, start=1)
        ]
        return Answer(
            question=question,
            answer=text.strip(),
            sources=sources,
            intents=result.intents,
            fallback=result.fallback,
            grounded=bool(cited),
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "RagPipeline":
        from .embedding import SentenceTransformerEmbedder
        from .generate import HFGenerator
        from .store import get_client

        return cls(
            get_client(settings),
            SentenceTransformerEmbedder(settings.embed_model),
            HFGenerator(settings.llm_model),
            settings.collection,
            settings.top_k,
        )
