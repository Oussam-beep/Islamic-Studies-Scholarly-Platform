"""Intent routing and filtered vector search.

A hand-written keyword router maps the question to source types (Qur'an, hadith, fiqh,
tafsir, fatwa) and extracts verse references ("2:255", "verse 4"). The result is a
Qdrant payload filter applied *before* vector ranking, so a question about a verse is not
answered from a fatwa. If the filter returns nothing (for example tafsir was not indexed)
the search falls back to an unfiltered query and says so.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from qdrant_client import QdrantClient, models

from .embedding import Embedder

INTENT_KEYWORDS: dict[str, list[str]] = {
    "Quran": ["quran", "surah", "ayah", "verse", "verses", "sura", "chapter", "recitation",
              "قرآن", "سورة", "آية", "اية", "آيات", "تلاوة", "كتاب الله"],
    "Hadith": ["hadith", "sunnah", "prophet", "narrated", "messenger", "bukhari", "muslim", "sahih",
               "حديث", "سنة", "النبي", "رسول", "رواه", "البخاري", "مسلم", "صحيح"],
    "Fiqh": ["fiqh", "jurisprudence", "madhhab", "school of thought", "hanafi", "shafii", "shafi'i",
             "maliki", "hanbali", "ruling", "permissible", "forbidden", "halal", "haram",
             "فقه", "مذهب", "حنفي", "شافعي", "مالكي", "حنبلي", "حكم", "جائز", "حرام", "حلال"],
    "Tafsir": ["tafsir", "tafseer", "interpretation", "exegesis", "commentary", "explanation of",
               "تفسير", "تأويل", "شرح آية"],
    "Fatwa": ["fatwa", "fatawa", "scholar", "opinion", "question", "answer", "consult",
              "فتوى", "فتاوى", "عالم", "رأي", "سؤال", "جواب", "استفتاء"],
}
INTENT_TO_SOURCE = {"Quran": "quran", "Hadith": "hadith", "Fiqh": "fiqh", "Tafsir": "tafsir", "Fatwa": "fatwa"}

_COLON_REF = re.compile(r"(?<!\d)(\d{1,3}):(\d{1,3})(?!\d)")
_VERSE_NO = re.compile(r"(?:verse|ayah|aya|no\.|number)\s*(\d+)")


def _contains(query_lower: str, keyword: str) -> bool:
    """ASCII keywords match at a word start (so 'verse' does not fire on 'universe')."""
    if keyword.isascii():
        return re.search(rf"\b{re.escape(keyword)}", query_lower) is not None
    return keyword in query_lower


def detect_intents(query: str) -> dict[str, bool]:
    q = query.lower()
    return {name: any(_contains(q, k) for k in kws) for name, kws in INTENT_KEYWORDS.items()}


def build_filter(query: str, intents: dict[str, bool]) -> models.Filter | None:
    must: list[models.Condition] = []

    colon = _COLON_REF.search(query)
    if colon and int(colon.group(1)) <= 114 and int(colon.group(2)) <= 286:
        key = f"{int(colon.group(1))}:{int(colon.group(2))}"
        must.append(models.FieldCondition(key="metadata.ayah_key", match=models.MatchValue(value=key)))
    else:
        verse = _VERSE_NO.search(query.lower())
        # a bare "number 53" must not hide hadith, so only apply with a Qur'an intent
        if verse and intents.get("Quran"):
            must.append(
                models.FieldCondition(key="metadata.ayah_number", match=models.MatchValue(value=int(verse.group(1))))
            )

    types = sorted({INTENT_TO_SOURCE[name] for name, on in intents.items() if on})
    if types:
        must.append(models.FieldCondition(key="metadata.source_type", match=models.MatchAny(any=types)))
    return models.Filter(must=must) if must else None


@dataclass
class Hit:
    ref: str
    source_type: str
    text: str
    score: float
    meta: dict = field(default_factory=dict)


@dataclass
class SearchResult:
    hits: list[Hit]
    intents: list[str]
    filtered: bool          # a payload filter was applied
    fallback: bool          # the filter matched nothing; results are from an unfiltered search


def _query(client: QdrantClient, collection: str, vector: list[float], flt, limit: int) -> list[Hit]:
    res = client.query_points(
        collection_name=collection, query=vector, query_filter=flt, limit=limit, with_payload=True
    )
    hits = []
    for p in res.points:
        payload = p.payload or {}
        meta = dict(payload.get("metadata", {}))
        hits.append(
            Hit(
                ref=meta.get("provenance_ref", "Unknown source"),
                source_type=meta.get("source_type", "unknown"),
                text=payload.get("page_content", ""),
                score=float(p.score),
                meta=meta,
            )
        )
    return hits


def search(client: QdrantClient, embedder: Embedder, query: str, collection: str, limit: int = 5) -> SearchResult:
    intents = detect_intents(query)
    flt = build_filter(query, intents)
    vector = embedder.embed_query(query)

    hits = _query(client, collection, vector, flt, limit)
    fallback = False
    if not hits and flt is not None:
        hits = _query(client, collection, vector, None, limit)
        fallback = bool(hits)
    return SearchResult(
        hits=hits,
        intents=[name for name, on in intents.items() if on],
        filtered=flt is not None and not fallback,
        fallback=fallback,
    )
