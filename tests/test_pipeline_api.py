from fastapi.testclient import TestClient

from islamic_rag.api import create_app
from islamic_rag.pipeline import Answer, SourceOut


class FakePipeline:
    def ask(self, question, top_k=5):
        return Answer(
            question=question,
            answer="Example response [Source 1].",
            sources=[SourceOut(1, "Quran 2:255", "quran", "Example source passage.", 0.9, True)],
            intents=["quran"],
            fallback=False,
            grounded=True,
        )


def test_health_endpoint_does_not_load_pipeline_early():
    client = TestClient(create_app(lambda: FakePipeline()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["pipeline_loaded"] is False


def test_ask_returns_source_metadata():
    client = TestClient(create_app(lambda: FakePipeline()))
    response = client.post("/ask", json={"question": "What is verse 2:255?", "top_k": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["sources"][0]["ref"] == "Quran 2:255"
    assert payload["sources"][0]["cited"] is True
    assert payload["grounded"] is True
