# src/query/intent_selector.py

import os
import json
from typing import Dict, List
from groq import Groq

# Groq client for high-capacity semantic reasoning
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Large model used because intent equivalence requires nuanced reasoning
MODEL = "llama-3.3-70b-versatile"


def _clean_llm_json(text: str) -> str:
    """
    Cleans common LLM formatting artifacts so JSON parsing succeeds.

    Handles:
    • Markdown code blocks
    • Leading 'json' tokens
    • Extra text before JSON starts
    """
    if not text:
        return ""

    text = text.strip()

    # Remove ``` wrappers if present
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()

    # Remove leading "json" label sometimes added by models
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Trim anything before first JSON object
    first = text.find("{")
    if first != -1:
        text = text[first:]

    return text.strip()


def select_best_intents(
    subqueries: List[str],
    candidates_by_subquery: Dict[str, Dict[str, str]],
) -> Dict[str, str | None]:
    """
    INTENT MATCHING ENGINE
    ======================

    Determines whether a previously stored research query
    is semantically equivalent to the current sub-query.

    Purpose:
    Prevents redundant web searches by reusing existing summaries
    when the *research intent* is effectively the same.

    This is NOT similarity scoring — this is strict semantic equivalence.

    Parameters
    ----------
    subqueries : List[str]
        Newly generated research questions.

    candidates_by_subquery : Dict
        For each sub-query (Q1, Q2, ...), contains a set of
        vector-retrieved past queries.

    Returns
    -------
    Dict[str, str | None]
        Mapping:
            Q1 → VS_02   (reuse this stored query)
            Q2 → None    (no equivalent found)
    """

    blocks = []

    # Build structured comparison blocks for each sub-query
    for i, sq in enumerate(subqueries, 1):
        qkey = f"Q{i}"
        cands = candidates_by_subquery.get(qkey, {})

        # Candidate list for the model to compare against
        cand_block = (
            "\n".join(f"{cid}: {ctext}" for cid, ctext in cands.items())
            if cands else
            "NONE"
        )

        blocks.append(
            f"""
SUB-QUERY {qkey}:
{sq}

CANDIDATE QUESTIONS:
{cand_block}
""".strip()
        )

    blocks_text = "\n\n".join(blocks)

    # Prompt enforces strict equivalence logic
    prompt = f"""
You are comparing research questions.

TASK:
For each sub-query, decide whether any candidate question
is essentially asking the SAME question.

IMPORTANT:
- Treat BOTH the sub-query and candidate as plain questions.
- Do NOT assume usefulness or relevance.
- Do NOT generalize or abstract.
- Do NOT match based on vague overlap.

DECISION RULE:
Select a candidate ONLY if a careful human reader would say:
“Yes — these two questions are basically asking the same thing.”

If they are not clearly the same, return null.

RULES:
- Select at most ONE ID per sub-query
- You MAY return null
- Do NOT reuse the same ID more than once
- Use ONLY the provided IDs
- Do NOT explain
- Return JSON ONLY

{blocks_text}

OUTPUT FORMAT:
{{
  "Q1": "VS_02",
  "Q2": null
}}
""".strip()

    # Send request to LLM
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # Deterministic reasoning
        max_tokens=400,
    )

    raw = r.choices[0].message.content or ""

    # Clean model output to ensure valid JSON
    cleaned = _clean_llm_json(raw)

    try:
        parsed = json.loads(cleaned)
    except Exception:
        # Fail-safe: assume no reusable intent if parsing fails
        return {f"Q{i+1}": None for i in range(len(subqueries))}

    # Ensure all keys exist
    for i in range(len(subqueries)):
        parsed.setdefault(f"Q{i+1}", None)

    return parsed
