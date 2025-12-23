"""Routing (skeleton).

Rule-first routing for interpretability and reliability.
"""

from __future__ import annotations
import re
from dataclasses import dataclass

_SURAH_AYAH_RE = re.compile(r"(?P<surah>\d{1,3})\s*[:/\-]\s*(?P<ayah>\d{1,3})")

@dataclass
class Route:
    name: str
    payload: dict

def route_query(q: str) -> Route:
    q = (q or "").strip()
    m = _SURAH_AYAH_RE.search(q)
    if m:
        return Route("direct_quran_ref", {"surah": int(m.group("surah")), "ayah": int(m.group("ayah"))})
    if q.lower().startswith("translate:"):
        return Route("translation", {"text": q[len("translate:"):].strip()})
    return Route("rag", {"query": q})
