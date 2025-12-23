# ID Conventions (Stable, Citation-Friendly)

## Source IDs (book/work level)
- Qur’an: `QUR:TANZIL-UTHMANI`
- Hadith: `HAD:bukhari`, `HAD:muslim`, ...
- Tafsir: `TAF:ibn_kathir`, `TAF:tabari`, `TAF:lisan_al_bayan`, `TAF:mukhtasar`
- Fatwa: `FAT:islamweb` (example; verify rights)

## Segment IDs (retrieval unit level)
- Qur’an ayah: `QUR:<surah>:<ayah>`
- Qur’an word: `QUR:<surah>:<ayah>:w<index>`
- Tafsir chunk: `TAF:<tafsir_id>:<surah>:<ayah>:c<chunk>`
- Hadith: `HAD:<collection>:b<book>:h<hadith_number>`
- Fatwa: `FAT:<source>:<doc_id>`

Segment IDs must be deterministic from references (not from array indices).
