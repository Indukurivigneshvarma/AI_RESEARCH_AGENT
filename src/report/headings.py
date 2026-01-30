import os
import json
from typing import List, Dict
from groq import Groq

# --------------------------------------------------
# LLM Client Setup
# --------------------------------------------------
# This module uses a large Groq-hosted model to generate
# the STRUCTURAL OUTLINE of the final research report.
# It does NOT write the report content — only:
#   • Title
#   • Section headings
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def generate_title_and_headings(
    user_query: str,
    summaries: List[str],
    max_topics: int = 3,
) -> Dict[str, List[str]]:
    """
    REPORT STRUCTURE GENERATOR
    ==========================

    Purpose
    -------
    Produces the **high-level structure** of the final research report:
        1. A formal academic title
        2. A list of section headings

    This function is part of the REPORT GENERATION stage and ensures:
        • Structural consistency
        • Academic tone
        • Alignment with the research question
        • No hallucinated scope expansion

    Inputs
    ------
    user_query : str
        The original research question (PRIMARY anchor).

    summaries : List[str]
        Evidence summaries collected during discovery.
        Used as SECONDARY signals to shape topical headings.

    max_topics : int
        Number of main topical sections to generate
        (excluding Executive Summary, Conclusion, References).

    Output Format
    -------------
    {
        "title": "Formal Academic Title",
        "headings": [
            "Executive Summary",
            "Topic 1",
            "Topic 2",
            ...
            "Conclusion",
            "References"
        ]
    }

    Design Philosophy
    -----------------
    • Title is query-driven (prevents scope drift)
    • Headings are evidence-informed (grounded in summaries)
    • Structure is standardized for downstream report writer
    """

    # Combine summaries into a simple bullet block for the LLM
    # This gives topical signals without allowing free-form expansion
    summary_block = "\n".join(f"- {s}" for s in summaries)

    # --------------------------------------------------
    # Prompt: Constrained Structural Generation
    # --------------------------------------------------
    # The prompt tightly controls:
    #   • Title style
    #   • Heading count
    #   • Mandatory sections
    #   • No new scope
    prompt = f"""
You are generating the structural outline of an academic research report.

- The research question is the PRIMARY semantic anchor.
- The title MUST be derived directly from the research question.
- The summaries are SECONDARY and may only refine phrasing.
- Do NOT introduce new scope.

TASK:
1. Generate ONE formal academic report title.
2. Generate section headings.

TITLE RULES:
- One sentence
- Formal academic tone
- Declarative
- Close to the research question
- Not broader than the query
- No "A Study of" or similar phrases

HEADING RULES:
- Include exactly once:
  Executive Summary
  Conclusion
  References
- Generate EXACTLY {max_topics} topical headings
- Derived from summaries
- Academic, non-overlapping
- Title Case
- No numbering or markdown

OUTPUT JSON ONLY:
{{
  "title": "<title>",
  "headings": [
    "Executive Summary",
    "<Topical Heading 1>",
    "<Topical Heading 2>",
    "...",
    "Conclusion",
    "References"
  ]
}}

RESEARCH QUESTION:
{user_query}

SUMMARIES:
{summary_block}
""".strip()

    # LLM call to generate structured outline
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # Low temperature → more deterministic structure
        max_tokens=300,
    )

    raw = r.choices[0].message.content.strip()

    # --------------------------------------------------
    # Cleaning LLM formatting artifacts
    # --------------------------------------------------
    # Handles cases where model wraps JSON in ```json blocks
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    # Parse JSON output
    data = json.loads(raw)

    # Validate required structure
    if "title" not in data or "headings" not in data:
        raise ValueError("Invalid headings output")

    return data
