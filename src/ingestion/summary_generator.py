# src/ingestion/summary_generator.py

import os
from groq import Groq
from openai import OpenAI
from src.config import MAX_SUMMARY_TOKENS   # Token cap for summaries

# Models used for summarization
GROQ_MODEL = "llama-3.1-8b-instant"
OR_MODEL   = "meta-llama/llama-3.1-8b-instruct"

# Primary fast summarization provider
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Secondary provider for load balancing and diversity
or_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def generate_summary(
    raw_text: str,
    provider: str = "groq",
) -> str:
    """
    EVIDENCE-DENSE SUMMARY GENERATOR
    ================================

    Converts raw web text into a structured, factual summary.

    This function is designed to:
        • Maximize factual recall
        • Minimize hallucination
        • Preserve quantitative data
        • Produce report-ready text

    Two providers are used to:
        - Distribute API load
        - Reduce single-provider dependency
        - Introduce minor model variance

    Parameters
    ----------
    raw_text : str
        Extracted content from a source webpage.

    provider : str
        "groq" or "openrouter"
        Determines which LLM backend is used.

    Returns
    -------
    str
        A single-paragraph evidence summary.
    """

    provider = provider.lower().strip()

    # Highly constrained prompt to enforce factual extraction behavior
    prompt = f"""
Write ONLY the summary text.

This summary will be inserted directly into a research report.
Do NOT include introductions, explanations, labels, or meta commentary.

GOAL:
Produce a comprehensive, evidence-dense summary by extracting
all distinct claims, data points, roles, tasks, tools, trends,
and projections mentioned in the text.

REQUIREMENTS:
- Output EXACTLY ONE paragraph
- Aim for a thorough and complete summary of approximately
  1500–2000 characters, prioritizing recall over compression
- Do NOT overly compress related ideas into a single sentence
- Neutral, analytical tone
- Include all numbers, percentages, ranges, timelines,
  named studies, organizations, tools, and projections IF PRESENT
- Explicitly state when quantitative evidence is missing
- Do NOT say phrases like "this report", "this article",
  or "here is a summary"
- No bullet points, headings, lists, or line breaks
- No speculation
- Use ONLY the provided text

TEXT:
{raw_text}
""".strip()

    # Use OpenRouter if selected
    if provider == "openrouter":
        r = or_client.chat.completions.create(
            model=OR_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low creativity, high factuality
            max_tokens=MAX_SUMMARY_TOKENS
        )
        return r.choices[0].message.content.strip()

    # Default provider: Groq
    r = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=MAX_SUMMARY_TOKENS,
    )

    return r.choices[0].message.content.strip()
