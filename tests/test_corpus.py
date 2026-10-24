from islamic_rag.corpus import iter_quran


def test_quran_loader_keeps_source_reference_and_stable_id(tmp_path):
    source = tmp_path / "quran.json"
    source.write_text(
        '[{"source":{"ayah_key":"2:255","surah_name_en":"Al-Baqarah",'
        '"surah_name_ar":"البقرة","surah_number":2,"ayah_number":255},'
        '"text":{"arabic":"آية","english_translation":"Verse"}}]',
        encoding="utf-8",
    )

    passage = next(iter_quran(source))

    assert passage.ref == "Quran Al-Baqarah 2:255"
    assert passage.source_type == "quran"
    assert passage.meta["ayah_key"] == "2:255"
    assert passage.point_id == passage.point_id
