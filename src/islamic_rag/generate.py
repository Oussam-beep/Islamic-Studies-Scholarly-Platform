"""Prompt construction, citation parsing and the local LLM wrapper."""
from __future__ import annotations

import re
from typing import Protocol

from .search import Hit

ARABIC_SYSTEM_PROMPT = (
    "أنت مساعد متخصص في الدراسات الإسلامية. أجب عن السؤال باللغة العربية الفصحى فقط، "
    "اعتماداً على المصادر المرفقة وحدها.\n"
    "القواعد:\n"
    "1. استخدم المعلومات الموجودة في المصادر فقط ولا تضف من عندك.\n"
    "2. ضع بعد كل معلومة وسم المصدر مثل [المصدر 1].\n"
    "3. إذا لم تحتوِ المصادر على إجابة فقل صراحة إن المصادر لا تتضمن الإجابة.\n"
    "4. اذكر الأقوال المختلفة للمذاهب إن وُجدت ولا ترجّح بلا دليل.\n"
    "5. لا تستخدم أي لغة غير العربية."
)

ENGLISH_SYSTEM_PROMPT = (
    "You are an assistant specialised in Islamic studies. Answer the question using ONLY the "
    "provided sources.\n"
    "Rules:\n"
    "1. Use only information found in the sources; do not add outside knowledge.\n"
    "2. After each claim, add the source tag, e.g. [Source 1].\n"
    "3. If the sources do not contain the answer, say so explicitly.\n"
    "4. Report differing positions of the schools of thought when present; do not choose one without evidence.\n"
    "5. Answer in English only. Do NOT generate Chinese text."
)

NO_SOURCES_AR = "لم أجد مصادر ذات صلة بهذا السؤال في قاعدة المعرفة."
NO_SOURCES_EN = "No relevant sources were found for this question in the knowledge base."

_ARABIC_CHARS = re.compile(r"[\u0600-\u06FF]")
_CITATION = re.compile(r"\[(?:Source|المصدر)\s*(\d+)\]")


class Generator(Protocol):
    def generate(self, messages: list[dict[str, str]]) -> str: ...


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if _ARABIC_CHARS.match(c)) / len(letters) > 0.5


def build_context(hits: list[Hit]) -> str:
    blocks = []
    for i, h in enumerate(hits, start=1):
        content = " ".join(h.text.split())
        blocks.append(f"[Source {i}]: {h.ref}\nContent: {content}")
    return "\n\n".join(blocks)


def build_messages(question: str, hits: list[Hit]) -> list[dict[str, str]]:
    arabic = is_arabic(question)
    system = ARABIC_SYSTEM_PROMPT if arabic else ENGLISH_SYSTEM_PROMPT
    label_q, label_s = ("السؤال", "المصادر") if arabic else ("Question", "Sources")
    user = f"{label_s}:\n{build_context(hits)}\n\n{label_q}: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_citations(answer: str, n_sources: int) -> list[int]:
    """Source numbers cited in the answer, in order of first appearance, ignoring invalid ones."""
    seen: list[int] = []
    for m in _CITATION.finditer(answer):
        n = int(m.group(1))
        if 1 <= n <= n_sources and n not in seen:
            seen.append(n)
    return seen


class HFGenerator:
    """Local chat model through Hugging Face Transformers (default: Qwen2.5-7B-Instruct)."""

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        max_new_tokens: int = 1024,
        temperature: float = 0.3,
        repetition_penalty: float = 1.05,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, device_map="auto")
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty

    def generate(self, messages: list[dict[str, str]]) -> str:
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
        ).to(self.model.device)
        output = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=self.temperature,
            repetition_penalty=self.repetition_penalty,
        )
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
