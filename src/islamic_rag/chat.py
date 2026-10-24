"""Interactive command-line chat: ask a question, read the answer and the cited sources."""
from __future__ import annotations

import textwrap

from .config import Settings
from .pipeline import Answer, RagPipeline


def render(result: Answer) -> str:
    out = [result.answer, ""]
    if not result.grounded and result.sources:
        out.append("(!) The answer does not cite any retrieved source. Treat it with caution.\n")
    if result.fallback:
        out.append("(i) No passage matched the detected source type; showing general results.\n")
    shown = [s for s in result.sources if s.cited] or result.sources[:1]
    for s in shown:
        out.append(f"--- [Source {s.tag}] {s.ref}  ({s.source_type}, score {s.score:.3f}) ---")
        out.append(textwrap.shorten(" ".join(s.text.split()), width=900, placeholder=" ..."))
        out.append("")
    return "\n".join(out)


def main() -> None:
    print("Loading models (this can take a minute)...")
    pipeline = RagPipeline.from_settings(Settings.from_env())
    print("Ready. Ask in Arabic or English ('quit' to exit).\n")
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if question:
            print("\n" + render(pipeline.ask(question)) + "\n")


if __name__ == "__main__":
    main()
