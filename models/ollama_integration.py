from langchain_ollama import OllamaLLM
from guardrails import Guard
import os
import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def get_ollama_response(prompt: str, model: str = "mistral"):
    llm = OllamaLLM(model=model)
    return llm.invoke(prompt)

def get_validated_response(
    context: str | list[str],
    question: str,
    rail_path: str = os.path.join(os.path.dirname(__file__), "..", "guardrails", "contradiction_output.rail"),
):
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
                contradicting_pairs.append({
                    "text_1": s1,
                    "text_2": s2,
                    "reason": "Numeric values differ"
                })

    guard = Guard.from_rail(rail_path)

    prompt = f"""
You are an expert contradiction detector.

Given a body of text, compare all sentence pairs and identify clear contradictions between them. A contradiction means:
- Two statements that cannot be true at the same time
- Conflicting facts, numbers, dates, rules, outcomes, or policies
- Opposing obligations, permissions, or conclusions

You must ignore:
- Reworded sentences that mean the same thing
- Stylistic or tone differences
- Vague or subjective statements

Your job is to return only direct, factual or logical contradictions in strict JSON format.

Example:
Context:
- "The city allows 10 days of water usage in summer."
- "Water usage is banned in summer."

Output:
{{
  "conflict_found": true,
  "conflict_pairs": [
    {{
      "text_1": "The city allows 10 days of water usage in summer.",
      "text_2": "Water usage is banned in summer.",
      "reason": "One permits summer water use, the other bans it"
    }}
  ]
}}

Now analyze:
Context:
{context}

Question:
{question}
"""

    raw_output = get_ollama_response(prompt)
    outcome = guard.parse(raw_output)

    if isinstance(outcome, tuple):
        outcome = outcome[0]
    if hasattr(outcome, "validated_output") and outcome.validated_output is not None:
        return outcome.validated_output
    if hasattr(outcome, "as_dict") and outcome.as_dict() is not None:
        return outcome.as_dict()
    if isinstance(outcome, dict):
        return outcome

    return {
        "conflict_found": False,
        "conflict_pairs": []
    }
