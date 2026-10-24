from islamic_rag.search import build_filter, detect_intents


def test_detect_intents_for_quran_and_hadith():
    intents = detect_intents("Is there a hadith about Qur'an verse 2:255?")
    assert intents["quran"]
    assert intents["hadith"]


def test_general_question_has_no_forced_source_filter():
    intents = detect_intents("What makes a good habit?")
    assert build_filter("What makes a good habit?", intents) is None
