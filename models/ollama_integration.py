from langchain_ollama import OllamaLLM
from guardrails import Guard

import os
import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


def get_ollama_response(prompt: str, model: str = "mistral"):
    """Simple helper to call an Ollama model and return the raw string."""
    llm = OllamaLLM(model=model)
    return llm.invoke(prompt)


def get_validated_response(
    context: str | list[str],
    question: str,
    rail_path: str = os.path.join(os.path.dirname(__file__), "..", "guardrails", "contradiction_output.rail"),

):
    """Detect contradictions either via fast numeric check or Guardrails‑validated LLM output."""

    from nltk.tokenize import sent_tokenize
    import re

    if isinstance(context, list):
        context = "\n".join(context)

    sentences = sent_tokenize(context)
    contradicting_pairs: list[dict] = []

    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            s1, s2 = sentences[i], sentences[j]
            nums1 = re.findall(r"\d+", s1)
            nums2 = re.findall(r"\d+", s2)
            if nums1 and nums2 and nums1 != nums2:
                contradicting_pairs.append(
                    {
                        "text_1": s1,
                        "text_2": s2,
                        "reason": "Numeric values differ",
                    }
                )

    # Commented to always run LLM+Guardrails
    # if contradicting_pairs:
    #     return {"conflict_found": True, "conflict_pairs": contradicting_pairs}

    # --------------------------
    # Guardrails + LLM fallback
    # --------------------------
    guard = Guard.from_rail(rail_path)

    prompt = f"""
You are an expert contradiction detector for HR policies.

Analyze the given texts and find **factual or logical contradictions**, especially in:
- Number of paid leave days
- Carry-forward leave rules
- Remote work during leave

Only respond in this format:
{{
  "conflict_found": true/false,
  "conflict_pairs": [
    {{
      "text_1": "...",
      "text_2": "...",
      "reason": "..."
    }}
  ]
}}

Context:
{context}

Question:
{question}
"""
    raw_output = OllamaLLM(model="mistral").invoke(prompt)
    print("Prompt sent to LLM:\n", prompt)
    print("Raw output from LLM:\n", raw_output)

    outcome = guard.parse(raw_output)
    if isinstance(outcome, tuple):
        outcome = outcome[0]

    if hasattr(outcome, "validated_output"):
        return outcome.validated_output
    if hasattr(outcome, "as_dict"):
        return outcome.as_dict()

    return outcome
