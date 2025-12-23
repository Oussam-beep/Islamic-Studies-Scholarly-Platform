# Project Constitution: Islamic Studies Scholarly Platform


## Objectives
Build a scholar-oriented platform combining vetted corpora + RAG to deliver:
- provenance-first chatbot for research assistance
- in-context search over Qur’ān, ḥadīth, tafsīr, fiqh, fatāwā
- bilingual translation (Arabic→English)
- word-sense disambiguation (WSD)
- speech-to-text (Arabic)
- low-resource inference modes (quantization/distillation)

## Trust rules
- **Cite exact passages** (segment IDs).
- If retrieval is empty or weak: **refuse** or return “evidence only”.
- Present **multiple interpretations** when sources differ.
- Fatwā-like prescriptive rulings: **do not issue definitive verdicts**; escalate to qualified jurists.

## Required platform features
- Provenance registry (source IDs, licenses, retrieval URLs, editions)
- Audit logs for every answer (query, retrieved segments, model version)
- Human-in-the-loop review queue (flag/correct outputs)

