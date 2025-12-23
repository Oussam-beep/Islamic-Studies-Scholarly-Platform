"""Corpus builder (skeleton).

Input: your current JSON files in data/raw/*
Output: normalized JSONL in data/processed/* suitable for indexing.

You will adapt loaders to match your current file formats.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Iterable
from .id import quran_ayah_id, quran_word_id

def iter_quran_ayah_segments(quran_json_path: Path) -> Iterable[Dict[str, Any]]:
    data = json.loads(quran_json_path.read_text(encoding="utf-8"))
    for surah_obj in data:
        surah = int(surah_obj["surah_number"])
        for ay in surah_obj.get("ayat", []):
            ayah = int(ay["ayah_number"])
            seg = {
                "segment_id": quran_ayah_id(surah, ayah),
                "source_id": "QUR:TANZIL-UTHMANI",
                "type": "quran_ayah",
                "ref": {"surah": surah, "ayah": ayah},
                "text": {"ar": ay["text"]["arabic"], "en": ay["text"].get("english", "")},
                "meta": {
                    "topics": ay.get("topics", []),
                    "related_ayat": ay.get("related_ayat", [])
                }
            }
            yield seg

def iter_quran_word_segments(quran_json_path: Path) -> Iterable[Dict[str, Any]]:
    data = json.loads(quran_json_path.read_text(encoding="utf-8"))
    for surah_obj in data:
        surah = int(surah_obj["surah_number"])
        for ay in surah_obj.get("ayat", []):
            ayah = int(ay["ayah_number"])
            for w in ay.get("analysis", {}).get("word_by_word", []):
                idx = int(w["word_index"])
                seg = {
                    "segment_id": quran_word_id(surah, ayah, idx),
                    "source_id": "QUR:TANZIL-UTHMANI",
                    "type": "quran_word",
                    "ref": {"surah": surah, "ayah": ayah, "word_index": idx},
                    "text": {"ar": w.get("arabic",""), "en": w.get("english","")},
                    "meta": {"irab": w.get("irab","")}
                }
                yield seg

def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main() -> None:
    raw = Path("data/raw")
    out = Path("data/processed")
    quran_path = raw / "quran" / "quran.json"
    if not quran_path.exists():
        raise SystemExit("Missing data/raw/quran/quran.json (put your file there)")
    write_jsonl(out/"quran"/"ayah.jsonl", iter_quran_ayah_segments(quran_path))
    write_jsonl(out/"quran"/"words.jsonl", iter_quran_word_segments(quran_path))
    print("Done: wrote Quran segments.")

if __name__ == "__main__":
    main()
