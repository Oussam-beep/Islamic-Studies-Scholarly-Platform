"""Load corpus sources into normalized, provenance-bearing passages."""
from __future__ import annotations
import argparse
import itertools
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator
import ijson

SOURCE_TYPES = ("quran", "hadith", "fiqh", "fatwa", "tafsir")
DEFAULT_SOURCES = ("quran", "hadith", "fiqh", "fatwa")
TAFSIR_BOOKS = {
    "ibn_kathir": ("ibn_kathir.json", "Tafsir Ibn Kathir"),
    "al_tabari": ("al_tabari.json", "Tafsir al-Tabari"),
    "al_qurtubi": ("al_qurtubi.json", "Tafsir al-Qurtubi"),
    "tahrir_al_tanwir": ("tahrir_al_tanwir.json", "Tafsir al-Tahrir wa al-Tanwir"),
    "al_razi": ("al_razi.json", "Tafsir al-Razi"),
    "al_muyassar": ("al_muyassar.json", "Tafsir al-Muyassar"),
    "al_mukhtasar": ("al_mukhtasar.json", "Tafsir al-Mukhtasar"),
    "as_saadi": ("as_saadi.json", "Tafsir as-Saadi"),
    "jalalayn": ("jalalayn.json", "Tafsir al-Jalalayn"),
}
_NAMESPACE = uuid.UUID("6f1f3c5e-0c3b-4a53-9a43-7d5a1b8e2c11")

@dataclass(frozen=True)
class Passage:
    """One retrievable source passage and its provenance metadata."""
    key: str
    text: str
    ref: str
    source_type: str
    meta: dict = field(default_factory=dict)

    @property
    def point_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, self.key))

def _clean(value: object) -> str:
    return str(value or "").strip()

def iter_quran(path: str | Path) -> Iterator[Passage]:
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    for record in records:
        source, text = record.get("source", {}), record.get("text", {})
        arabic = _clean(text.get("arabic"))
        key = _clean(source.get("ayah_key"))
        if not arabic or not key:
            continue
        surah_en = _clean(source.get("surah_name_en"))
        surah_ar = _clean(source.get("surah_name_ar"))
        number = int(source.get("ayah_number") or 0)
        english = _clean(text.get("english_translation"))
        yield Passage(
            key=f"quran:{key}",
            text=f"Quran Surah {surah_en} ({surah_ar}), Verse {number}.\nArabic: {arabic}\nTranslation: {english}",
            ref=f"Quran {surah_en} {key}", source_type="quran",
            meta={"surah_number": int(source.get("surah_number") or 0), "surah_name_en": surah_en,
                  "ayah_number": number, "ayah_key": key, "revelation_place": _clean(source.get("revelation_place"))},
        )

def iter_hadith(path: str | Path) -> Iterator[Passage]:
    with open(path, encoding="utf-8") as stream:
        data = json.load(stream)
    title = _clean(data.get("metadata", {}).get("english", {}).get("title")) or Path(path).stem
    for record in data.get("hadiths", []):
        english = record.get("english") or {}
        arabic, english_text = _clean(record.get("arabic")), _clean(english.get("text"))
        if not arabic and not english_text:
            continue
        hid = record.get("id", "")
        narrator = _clean(english.get("narrator"))
        yield Passage(
            key=f"hadith:{record.get('bookId', '')}:{hid}",
            text=f"Hadith Record ({title}).\nNarrated by: {narrator}\nText: {english_text}\nArabic: {arabic}",
            ref=f"Hadith: {title} #{hid}", source_type="hadith",
            meta={"collection": title, "hadith_id": hid, "id_in_book": record.get("idInBook"),
                  "chapter_id": record.get("chapterId"), "narrator": narrator},
        )

def iter_fiqh(path: str | Path) -> Iterator[Passage]:
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    for record in records:
        text, rid = _clean(record.get("content")), record.get("id", "")
        if text:
            yield Passage(key=f"fiqh:{rid}", text=f"Fiqh analysis: {text}",
                          ref=f"Fiqh source ID: {rid}", source_type="fiqh", meta={"chunk_id": rid})

def iter_fatwa(path: str | Path) -> Iterator[Passage]:
    with open(path, "rb") as stream:
        for index, record in enumerate(ijson.items(stream, "item")):
            title, question, answer = (_clean(record.get(k)) for k in ("title", "question", "answer"))
            if not answer:
                continue
            label = title if len(title) <= 60 else title[:57] + "..."
            yield Passage(key=f"fatwa:{index}",
                          text=f"Fatwa topic: {title}\nQuestion: {question}\nScholar answer: {answer}",
                          ref=f"Fatwa: {label}", source_type="fatwa", meta={"title": title, "record_index": index})

def iter_tafsir(path: str | Path, book_id: str, title: str) -> Iterator[Passage]:
    with open(path, "rb") as stream:
        for surah in ijson.items(stream, "item"):
            for ayah in surah.get("ayat", []):
                key = _clean(ayah.get("verse_key"))
                parts = []
                for item in ayah.get("tafsir", []):
                    text = item.get("text") or {}
                    parts.extend((_clean(text.get("arabic")), _clean(text.get("english"))))
                body = "\n".join(part for part in parts if part)
                if not key or not body:
                    continue
                yield Passage(key=f"tafsir:{book_id}:{key}",
                              text=f"Tafsir ({title}) for Quran {key}\nTafsir: {body}",
                              ref=f"Tafsir: {title} {key}", source_type="tafsir",
                              meta={"tafsir_book": book_id, "ayah_key": key,
                                    "ayah_number": int(ayah.get("ayah_number") or 0),
                                    "surah_number": int(surah.get("surah_number") or 0)})

def iter_corpus(data_dir: str | Path, sources: Iterable[str] = DEFAULT_SOURCES,
                tafsir_books: Iterable[str] = (), limit: int | None = None) -> Iterator[Passage]:
    """Yield selected sources. `limit` caps records per source file for quick trials."""
    directory, selected = Path(data_dir), set(sources)
    unknown = selected - set(SOURCE_TYPES)
    if unknown:
        raise ValueError(f"unknown sources: {sorted(unknown)}")
    def cap(iterator: Iterator[Passage]) -> Iterator[Passage]:
        return itertools.islice(iterator, limit) if limit is not None else iterator
    if "quran" in selected:
        yield from cap(iter_quran(directory / "quran.json"))
    if "hadith" in selected:
        for name in ("bukhari_merged.json", "muslim_merged.json"):
            yield from cap(iter_hadith(directory / "Hadith" / name))
    if "fiqh" in selected:
        yield from cap(iter_fiqh(directory / "Fiqh.json"))
    if "fatwa" in selected:
        yield from cap(iter_fatwa(directory / "Fatwa.json"))
    for book_id in tafsir_books:
        if book_id not in TAFSIR_BOOKS:
            raise ValueError(f"unknown tafsir book: {book_id}")
        filename, title = TAFSIR_BOOKS[book_id]
        yield from cap(iter_tafsir(directory / "TAFASIR" / "books" / filename, book_id, title))

def main() -> None:
    parser = argparse.ArgumentParser(description="Count passages per source in a data folder.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--sources", nargs="+", default=list(DEFAULT_SOURCES), choices=list(DEFAULT_SOURCES))
    parser.add_argument("--tafsir-books", nargs="*", default=[], choices=sorted(TAFSIR_BOOKS))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    counts: dict[str, int] = {}
    for passage in iter_corpus(args.data_dir, args.sources, args.tafsir_books, args.limit):
        counts[passage.source_type] = counts.get(passage.source_type, 0) + 1
    for name, count in counts.items():
        print(f"{name:8s} {count:8,}")
    print(f"{'total':8s} {sum(counts.values()):8,}")

if __name__ == "__main__":
    main()