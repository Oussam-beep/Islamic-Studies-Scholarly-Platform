"""Citation watchdog (skeleton).

Goal: ensure every answer paragraph is supported by segment IDs.
"""

from __future__ import annotations
from typing import List, Dict

def validate_citations(answer: Dict) -> List[str]:
    errors: List[str] = []
    # Expect answer to include: answer['used_segments'] and answer['paragraphs'][i]['citations']
    used = set(answer.get("used_segments", []))
    for i, p in enumerate(answer.get("paragraphs", [])):
        cites = set(p.get("citations", []))
        if not cites:
            errors.append(f"Paragraph {i} missing citations")
        if cites and not cites.issubset(used):
            errors.append(f"Paragraph {i} cites segments not in used_segments")
    return errors
