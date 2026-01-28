import os
import json
from typing import List, Dict
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def generate_title_and_headings(
    user_query: str,
    summaries: List[str],
    max_topics: int = 3,
) -> Dict[str, List[str]]:

    summary_block = "\n".join(f"- {s}" for s in summaries)

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

    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )

    raw = r.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    data = json.loads(raw)

    if "title" not in data or "headings" not in data:
        raise ValueError("Invalid headings output")

    return data
