import os
from typing import Dict, List
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-70b-instruct"
)


def write_report(
    title: str,
    headings: List[str],
    summaries: Dict[str, str],
    references: List[str],
) -> str:

    summary_block = "\n".join(
        f"{sid}: {text}"
        for sid, text in summaries.items()
    )

    heading_block = "\n".join(
        f"@@{h}@@" for h in headings
    )

    refs_block = "\n".join(references)

    prompt = f"""
You are writing an academic research synthesis.

YOU MUST FOLLOW THE FORMAT EXACTLY.

FORMAT RULES:
- Use ONLY the headings provided.
- Each heading MUST appear exactly once.
- Headings wrapped as @@Heading@@
- Title wrapped as:
  @@TITLE@@
  <title>
  @@TITLE@@
- Plain text only.
- No markdown.
- No bullet points.

CITATION RULES:
- EVERY declarative sentence must end with citation markers.
- Format: [S1] or [S1][S3]
- No paragraph-level citations.
- No uncited sentences except References.

CONTENT RULES:
- Only use facts from summaries.
- You may paraphrase or synthesize.
- Do not introduce new facts.
- State uncertainty if evidence is weak.

- Executive Summary: 5–6 sentences.
- Each topical section: 2–3 paragraphs, 4–5 sentences each.
- Conclusion: 5–6 synthesis sentences.

REFERENCES RULE:
- At @@References@@ output EXACT reference list provided.
- Do not modify references.

INPUTS:

TITLE:
{title}

HEADINGS:
{heading_block}

SUMMARIES:
{summary_block}

REFERENCES:
{refs_block}

OUTPUT:
Return the COMPLETE report using the exact format.
""".strip()

    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2500,
    )

    return r.choices[0].message.content.strip()
