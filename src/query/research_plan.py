# src/query/research_plan.py

import os
import json
import cohere
from typing import Dict, List

# Cohere client used for structured reasoning tasks
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Model selected for decomposition and structured planning
MODEL = "command-a-03-2025"


def generate_research_plan(user_query: str) -> Dict[str, List[str]]:
    """
    RESEARCH PLANNING ENGINE
    ========================

    This is the *conceptual starting point* of the entire system.

    Instead of immediately searching the web, the system first:
        • Interprets the user’s research question
        • Converts it into a structured research goal
        • Breaks it into key conceptual dimensions

    These dimensions define the scope of investigation and guide
    all downstream discovery and evaluation steps.

    Parameters
    ----------
    user_query : str
        The original research question entered by the user.

    Returns
    -------
    Dict with:
        "goal"       → normalized research objective
        "dimensions" → list of conceptual coverage areas
    """

    # Prompt designed to force structured reasoning, not free text
    prompt = f"""
You are a research planning assistant.

TASK:
Decompose the research question into high-level conceptual dimensions
that must be covered to answer it thoroughly.

RULES:
- Dimensions are NOT search queries
- Dimensions represent themes, angles, or aspects
- Be domain-agnostic
- Avoid redundancy or overlap
- Produce 4–6 dimensions
- Do NOT explain anything

OUTPUT FORMAT (JSON ONLY):
{{
  "goal": "<rephrased research goal>",
  "dimensions": [
    "Dimension 1",
    "Dimension 2"
  ]
}}

RESEARCH QUESTION:
{user_query}
""".strip()

    # Call Cohere model to generate plan
    r = co.chat(
        model=MODEL,
        message=prompt,
        temperature=0.3,  # Low temperature → structured, less creative
        max_tokens=400,
    )

    raw = r.text.strip()

    # Handle cases where model wraps JSON in markdown
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    # Parse structured output
    data = json.loads(raw)

    # Safety validation to ensure required fields exist
    if "goal" not in data or "dimensions" not in data:
        raise ValueError("Invalid research plan output")

    return data
