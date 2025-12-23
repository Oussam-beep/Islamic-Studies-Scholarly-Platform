# Data Model Overview

This platform uses two representations:

1) **Raw / canonical** (human-friendly): as collected.
2) **Processed / index-ready**: JSONL segments, one record per retrieval chunk.

## Required registries
- `data/registry/sources.json` (book-level metadata + provenance)
- `data/registry/licenses.json`

## Processed segments
All searchable content is stored as JSONL of a common schema:
- `segment_id` (stable)
- `source_id` (book/work)
- `type` (quran_ayah, hadith, tafsir, fatwa, fiqh, ...)
- `ref` (structured reference fields)
- `text` (ar/en)
- `meta` (optional: topics, madhhab, isnad, grading, links)

