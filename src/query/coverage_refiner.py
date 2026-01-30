# src/query/coverage_refiner.py

import os
import cohere
from typing import Dict, List

# Initialize Cohere client using API key from environment
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Model chosen for structured reasoning and gap analysis
MODEL = "command-a-03-2025"


def refine_queries(
    research_plan: Dict[str, List[str]],
    summaries: Dict[str, str],
    n_queries: int = 2,
) -> List[str]:
    """
    COVERAGE REFINEMENT ENGINE
    ===========================

    This module is responsible for the *iterative intelligence* of the system.

    After the first discovery round, the system evaluates:
        • What has already been covered
        • Which research dimensions remain weak or missing

    It then asks an LLM to propose new sub-queries that expand coverage
    without repeating existing knowledge.

    Parameters
    ----------
    research_plan : Dict
        Contains:
            - goal
            - list of research dimensions

    summaries : Dict[str, str]
        Mapping of summary IDs → summary text
        Represents knowledge already collected.

    n_queries : int
        Number of new sub-queries to generate.

    Returns
    -------
    List[str]
        New targeted research queries for the next discovery iteration.
    """

    # Convert existing summaries into a structured block
    # so the LLM can see what evidence already exists
    summary_block = "\n".join(
        f"{sid}: {text}"
        for sid, text in summaries.items()
    )

    # Convert research dimensions into bullet list
    plan_block = "\n".join(
        f"- {d}" for d in research_plan.get("dimensions", [])
    )

    # Prompt designed to enforce strict, non-creative behavior.
    # It tells the model to behave like a research planner,
    # not a content generator.
    prompt = f"""
You are refining a research process.

TASK:
Given the research plan and summaries collected so far,
generate EXACTLY {n_queries} NEW search sub-queries that would
most improve coverage, depth, or clarity.

RULES:
- Queries must be suitable for academic web search
- Queries must target missing, weak, or underdeveloped dimensions
- Do NOT repeat existing summaries
- Do NOT explain
- One query per line
- No numbering
- Broad but precise

RESEARCH GOAL:
{research_plan.get("goal")}

RESEARCH DIMENSIONS:
{plan_block}

CURRENT SUMMARIES:
{summary_block}

OUTPUT:
Exactly {n_queries} lines, each a search query.
""".strip()

    # Send prompt to Cohere model
    r = co.chat(
        model=MODEL,
        message=prompt,
        temperature=0.4,   # Slight creativity but controlled
        max_tokens=200,
    )

    text = r.text

    # Clean and normalize output lines
    lines = [
        l.strip()
        for l in text.split("\n")
        if l.strip()
    ]

    # Safety check — ensures pipeline reliability
    if len(lines) < n_queries:
        raise ValueError("Coverage refiner returned too few queries")

    return lines[:n_queries]
