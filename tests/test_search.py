from islamic_rag.search import build_filter, detect_intents


def test_detect_intents_for_quran_and_hadith():
    intents = detect_intents("Is there a hadith about Qur'an verse 2:255?")
    assert intents["Quran"]
    assert intents["Hadith"]


def test_general_question_has_no_forced_source_filter():
    query = "What makes a good habit?"
    intents = detect_intents(query)
    assert build_filter(query, intents) is None
