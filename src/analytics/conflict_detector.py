# src/analytics/conflict_detector.py

import os
import json
from typing import List, Dict
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Fast reasoning model for logical contradiction analysis
MODEL = "gemini-flash-latest"


def _clean_llm_json(text: str) -> str:
    """
    Cleans LLM output so it can be safely parsed as JSON.

    Handles:
    • Markdown code fences
    • Leading 'json' tokens
    • Extraneous text before JSON object
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


def detect_conflicts(
    summaries: List[Dict[str, str]],
) -> Dict:
    """
    HARD FACTUAL CONFLICT DETECTOR
    ==============================

    Identifies logical contradictions between summaries.

    This is stricter than disagreement detection.
    A conflict is flagged ONLY when:
        • The claims refer to the same phenomenon
        • They cannot both be true simultaneously

    This ensures:
        • No false conflicts due to framing differences
        • No conflicts from complementary claims
        • No conflicts from missing information

    Parameters
    ----------
    summaries : List[Dict]
        Each summary contains:
            "id"
            "summary"

    Returns
    -------
    {
      "conflicts": [
        {
          "ids": ["S1", "S2"],
          "claim_a": "...",
          "claim_b": "..."
        }
      ]
    }
    """

    # Not enough summaries to compare
    if len(summaries) < 2:
        return {"conflicts": []}

    # Build comparison block for model
    block = "\n\n".join(
        f"{s['id']}:\n{s['summary']}"
        for s in summaries
    )

    # Prompt enforces strict logical contradiction criteria
    prompt = f"""
You are detecting HARD FACTUAL CONTRADICTIONS between research summaries.

DEFINITION (STRICT):
A factual contradiction exists ONLY if both claims refer to the same
phenomenon or variable AND they cannot logically be true at the same time
in the same real world.

CRITICAL TEST (MANDATORY):
Before marking a conflict, explicitly apply this test internally:
"If both claims were true simultaneously, would this create a logical
impossibility?"

If the answer is NO → DO NOT mark a conflict.

TASK:
Compare EACH summary against EVERY OTHER summary.
Identify ONLY hard contradictions that pass the above test.

DO NOT mark conflicts for:
- Different examples, lists, or enumerations
- Partial overlap of factors, causes, effects, or benefits
- Differences in emphasis, framing, categorization, or prioritization
- Additive or complementary claims
- Missing information in one summary
- Different scopes or levels of detail
- Descriptive vs analytical differences

MARK a conflict ONLY for:
- Direct numeric oppositions
- Mutually exclusive states or requirements
- Opposite trends or outcomes
- Explicit denial of the same factual claim

RULES:
- Output at most ONE conflict per summary pair
- Extract the exact conflicting claims verbatim
- Use ONLY information explicitly stated
- Do NOT infer, generalize, or invent facts
- Output JSON ONLY

OUTPUT FORMAT:
{{
  "conflicts": [
    {{
      "ids": ["S1", "S2"],
      "claim_a": "explicit factual claim from S1",
      "claim_b": "explicit factual claim from S2"
    }}
  ]
}}

If no hard contradictions exist:
{{ "conflicts": [] }}

SUMMARIES:
{block}
""".strip()

    # Call Gemini model
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)

    raw = response.text or ""
    cleaned = _clean_llm_json(raw)

    # Parse JSON response
    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Conflict detector returned invalid JSON:\n{cleaned}") from e
