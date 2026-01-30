# src/analytics/agreement_detector.py

import os
import json
from typing import List, Dict
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Fast reasoning model suitable for pairwise semantic analysis
MODEL = "gemini-flash-latest"

# Only these agreement relations are allowed
ALLOWED_LABELS = {
    "strongly_supports",
    "partially_supports",
    "independent",
}


def _clean_llm_json(text: str) -> str:
    """
    Cleans common LLM formatting artifacts before JSON parsing.

    Handles:
    • Markdown code blocks
    • Leading "json" token
    • Extra text before JSON object
    """
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    first_brace = text.find("{")
    if first_brace != -1:
        text = text[first_brace:]
    return text.strip()


def detect_agreements(
    summaries: List[Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    """
    CROSS-SOURCE AGREEMENT DETECTOR
    ===============================

    This module analyzes how evidence summaries relate to each other.

    It determines whether:
        • One summary strongly supports another
        • Only partial overlap exists
        • The summaries discuss independent information

    This enables *trust-weighted synthesis* later in the pipeline.

    Parameters
    ----------
    summaries : List[Dict]
        Each summary must contain:
            "id"
            "summary"

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping:
            S1 → { S2: "strongly_supports", S3: "independent" }
    """

    # Not enough data for comparison
    if len(summaries) < 2:
        return {}

    # Prepare structured block for model comparison
    block = "\n\n".join(
        f"{s['id']}:\n{s['summary']}"
        for s in summaries
    )

    # Prompt enforces rule-based agreement classification
    prompt = f"""
Analyze cross-source agreement.

Allowed labels ONLY:
- strongly_supports
- partially_supports
- independent

Rules:
- Compare EACH summary against EVERY OTHER summary
- Directional (A→B may differ from B→A)
- NO explanations
- Return JSON ONLY

SUMMARIES:
{block}

OUTPUT FORMAT:
{{
  "S1": {{ "S2": "strongly_supports" }}
}}
""".strip()

    # Run Gemini model
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)

    raw = response.text or ""
    cleaned = _clean_llm_json(raw)

    # Parse JSON output
    try:
        data = json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Agreement LLM returned invalid JSON:\n{cleaned}") from e

    # Validate structure strictly for system reliability
    ids = {s["id"] for s in summaries}

    for src, relations in data.items():
        if src not in ids:
            raise ValueError(f"Unknown source ID: {src}")
        if not isinstance(relations, dict):
            raise ValueError(f"Relations for {src} must be a dict")

        for tgt, label in relations.items():
            if tgt not in ids:
                raise ValueError(f"Unknown target ID: {tgt}")
            if src == tgt:
                raise ValueError("Self-relations are not allowed")
            if label not in ALLOWED_LABELS:
                raise ValueError(f"Invalid agreement label: {label}")

    return data
