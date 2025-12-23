"""ID generation rules: deterministic, citation-friendly, stable across rebuilds."""

from __future__ import annotations

def quran_ayah_id(surah: int, ayah: int) -> str:
    return f"QUR:{surah}:{ayah}"

def quran_word_id(surah: int, ayah: int, word_index: int) -> str:
    return f"QUR:{surah}:{ayah}:w{word_index}"

def tafsir_chunk_id(tafsir_id: str, surah: int, ayah: int, chunk: int) -> str:
    return f"TAF:{tafsir_id}:{surah}:{ayah}:c{chunk}"

def hadith_id(collection: str, book: int | None, hadith_number: int | str) -> str:
    # If you don't have book numbers, pass book=None and ensure hadith_number is unique in the collection.
    if book is None:
        return f"HAD:{collection}:{hadith_number}"
    return f"HAD:{collection}:b{book}:h{hadith_number}"

def fatwa_id(source: str, doc_id: str) -> str:
    return f"FAT:{source}:{doc_id}"
