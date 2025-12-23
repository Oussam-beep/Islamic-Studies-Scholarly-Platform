# Islamic Studies Scholarly Platform (RAG) — Project Template

This repository is a **provenance-first** Retrieval-Augmented Generation (RAG) platform for Islamic Studies:
Qur’ān, ḥadīth, tafsīr, fatāwā, translation, WSD, and speech-to-text.

## Principles (non-negotiable)
- Answers must be **grounded in retrieved passages**.
- **Citations are mandatory** (segment IDs + source metadata).
- The system surfaces **multiple interpretations** where sources differ.
- **No prescriptive fatāwā**: provide references and recommend qualified jurists.

See `PROJECT_SPEC.md` for the full project constitution.

## Quick Start (skeleton)
1. Put your original files in `data/raw/...`
2. Fill `data/registry/sources.json` and `data/registry/licenses.json`
3. Run the corpus builder (to implement): `python -m islamic_rag.data.build_corpus`
4. Build indexes (to implement): `python -m islamic_rag.retrieval.build_index`
5. Serve API/UI (to implement)

## Folder map
islamic-rag-platform/
├─ PROJECT_SPEC.md
├─ README.md
├─ pyproject.toml
├─ configs/
│  └─ pipeline.yaml
├─ data/
│  ├─ raw/                       #  ORIGINAL files 
│  │  ├─ quran/
│  │  │  └─ quran.json
│  │  ├─ hadith/
│  │  │  ├─ bukhari.json
│  │  │  ├─ muslim.json
│  │  │  ├─ book3.json
│  │  │  └─ book4.json
│  │  ├─ tafsir/
│  │  │  ├─ ibn_kathir.json
│  │  │  ├─ tabari.json
│  │  │  ├─ lisan_al_bayan.json
│  │  │  └─ mukhtasar.json
│  │  └─ fatwa/
│  │     └─ islamweb.json
│  │
│  ├─ registry/                  # REQUIRED for scholarly provenance
│  │  ├─ sources.json             # one entry per book/source
│  │  ├─ licenses.json            # reusable license objects
│  │  └─ NOTICE.md                # attribution + “how to cite” notes
│  │
│  ├─ processed/                  # index-ready JSONL segments (generated)
│  │  ├─ quran/
│  │  │  ├─ ayah.jsonl
│  │  │  ├─ words.jsonl
│  │  │  └─ ayah_ranges.jsonl     
│  │  ├─ hadith/
│  │  │  ├─ bukhari.jsonl
│  │  │  ├─ muslim.jsonl
│  │  │  ├─ book3.jsonl
│  │  │  └─ book4.jsonl
│  │  ├─ tafsir/
│  │  │  ├─ ibn_kathir.jsonl
│  │  │  ├─ tabari.jsonl
│  │  │  ├─ lisan_al_bayan.jsonl
│  │  │  └─ mukhtasar.jsonl
│  │  └─ fatwa/
│  │     └─ islamweb.jsonl
│  │
│  └─ eval/                       # gold sets + adversarial tests
│     ├─ gold_queries.jsonl
│     ├─ expected_citations.jsonl
│     └─ refusal_tests.jsonl
│
├─ schemas/                       # JSON Schemas (validation)
│  ├─ source.schema.json
│  ├─ segment.schema.json
│  └─ rag_response.schema.json
│
├─ indexes/                       # built artifacts (FAISS/BM25)
│  ├─ bm25/
│  └─ vectors/
│
├─ models/                        # downloaded LLM/embedding weights (optional)
│
├─ logs/                          # audit logs (query → evidence → answer)
│
├─ src/
│  └─ islamic_rag/
│     ├─ data/
│     │  ├─ id.py
│     │  ├─ chunking.py
│     │  ├─ validate.py
│     │  └─ build_corpus.py
│     ├─ retrieval/
│     │  ├─ build_index.py
│     │  └─ search.py
│     ├─ rag/
│     │  ├─ router.py
│     │  ├─ generate.py
│     │  ├─ prompts/
│     │  └─ watchdogs/
│     │     ├─ citations.py
│     │     └─ quote_match.py
│     ├─ translation/
│     ├─ wsd/
│     ├─ s2t/
│     ├─ eval/
│     └─ logging/
│
├─ scripts/                       # CLI wrappers
└─ tests/                         # unit tests for IDs, chunking, validators

- `data/raw/` original, unchanged dumps
- `data/processed/` index-ready JSONL segments
- `data/registry/` provenance + licensing registry (required)
- `schemas/` JSON Schemas for validation
- `src/islamic_rag/` pipeline code

