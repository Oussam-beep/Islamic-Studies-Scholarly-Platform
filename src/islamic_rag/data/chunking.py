"""Chunking helpers.

Goal: create retrieval segments that are not too long, and keep boundaries meaningful.
"""

from __future__ import annotations
import re
from typing import List

_ARABIC_SENTENCE_SPLIT = re.compile(r"(?<=[\.!؟\?؛؛:])\s+")
_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n+")

def split_paragraphs(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = [p.strip() for p in _PARAGRAPH_SPLIT.split(text) if p.strip()]
    return parts

def split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = [p.strip() for p in _ARABIC_SENTENCE_SPLIT.split(text) if p.strip()]
    return parts

def greedy_pack(units: List[str], max_chars: int) -> List[str]:
    """Character-based packing (simple, model-agnostic). Replace with token-based if needed."""
    chunks: List[str] = []
    buf: List[str] = []
    size = 0
    for u in units:
        if size + len(u) + 1 > max_chars and buf:
            chunks.append(" ".join(buf).strip())
            buf, size = [], 0
        buf.append(u)
        size += len(u) + 1
    if buf:
        chunks.append(" ".join(buf).strip())
    return chunks
