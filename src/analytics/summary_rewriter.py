# src/analytics/summary_rewriter.py

import os
import json
from typing import Dict
from groq import Groq

# --------------------------------------------------
# LLM setup
# --------------------------------------------------
# This module uses a fast Groq-hosted LLM to rewrite summaries
# after conflict resolution. The goal is to REMOVE only specific
# contradictory claims while preserving all other information.

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def rewrite_summaries(
    rewrite_plan: Dict[str, Dict[str, object]]
) -> Dict[str, str]:
    """
    SUMMARY REWRITING MODULE
    =========================

    This stage executes *surgical evidence correction*.

    Instead of deleting entire summaries when conflicts occur,
    only the specific losing claims are removed while keeping
    the rest of the evidence intact.

    Why an LLM is used:
        • Claims may be embedded in complex sentences
        • Direct string deletion can break grammar or meaning
        • Minor rephrasing may be required

    This ensures:
        - Evidence integrity
        - Logical consistency
        - Minimal information loss

    rewrite_plan format:
    {
        "S4": {
            "summary": "<original summary text>",
            "remove_claims": [
                "claim text 1",
                "claim text 2"
            ]
        },
        ...
    }

    Returns:
    {
        "S4": "<rewritten summary>",
        ...
    }
    """

    # No rewrite needed → return empty
    if not rewrite_plan:
        return {}

    # --------------------------------------------------
    # Build structured blocks for each summary
    # --------------------------------------------------

    blocks = []

    for sid, data in rewrite_plan.items():
        claims = "\n".join(f"- {c}" for c in data.get("remove_claims", []))

        blocks.append(
            f"""SUMMARY ID: {sid}

ORIGINAL SUMMARY:
{data["summary"]}

CLAIMS TO REMOVE:
{claims}"""
        )

    joined_blocks = "\n\n".join(blocks)

    # --------------------------------------------------
    # LLM Prompt Design
    # --------------------------------------------------
    # Prompt strictly forbids summarization, addition, or explanation.
    # The model acts like an editor, not a generator.

    prompt = f"""
You are editing research summaries.

TASK:
For EACH summary, rewrite it so that the listed claims are NO LONGER PRESENT.

IMPORTANT RULES:
- You MAY rewrite or rephrase sentences if needed to remove the ideas
- Keep all other content as close as possible to the original
- Preserve tone, scope, and level of detail
- Do NOT add new facts
- Do NOT summarize
- Do NOT explain your changes
- Do NOT invent information

OUTPUT FORMAT (JSON ONLY):
{{
  "rewritten": {{
    "S1": "rewritten summary text",
    "S2": "rewritten summary text"
  }}
}}

SUMMARIES:
{joined_blocks}
""".strip()

    # --------------------------------------------------
    # Run LLM rewrite
    # --------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,   # Deterministic editing
        max_tokens=2000,
    )

    content = response.choices[0].message.content.strip()

    # --------------------------------------------------
    # Parse strict JSON output
    # --------------------------------------------------

    try:
        data = json.loads(content)
    except Exception as e:
        raise ValueError(
            f"Summary rewriter returned invalid JSON:\n{content}"
        ) from e

    rewritten = data.get("rewritten")
    if not isinstance(rewritten, dict):
        raise ValueError("Missing or invalid 'rewritten' field")

    return rewritten
