# Local corpus setup

The corpus files are not committed to this repository. Acquire the materials separately and check source-specific licensing and attribution requirements before using or redistributing them.

## Expected layout

```text
data/raw/
├── quran.json
├── Fiqh.json
├── Fatwa.json
├── Hadith/
│   ├── bukhari_merged.json
│   └── muslim_merged.json
└── TAFASIR/
    └── books/
        └── <book-id>.json
```

The exact schema is defined by the loaders in `src/islamic_rag/corpus.py`. Confirm file names and required fields before indexing a different edition or dataset.

## Data hygiene

- Keep raw and processed data, embedding caches, and vector-store files out of Git.
- Do not commit source archives, credentials, model weights, or private data.
- Record source title, publisher/edition, source URL, acquisition date, license, and required attribution in a local source manifest.
- Start with a small corpus sample and manually inspect normalized passages and references before building a full index.
