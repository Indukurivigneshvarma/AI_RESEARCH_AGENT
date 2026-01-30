import os
from typing import Dict, List
from openai import OpenAI

# --------------------------------------------------
# LLM Client Setup (OpenRouter)
# --------------------------------------------------
# This module uses an OpenRouter-hosted large language model
# to generate the FINAL RESEARCH REPORT TEXT.
#
# Important:
# - This is NOT a creative writing step.
# - It is a *constrained synthesis* step.
# - The model is forced to use ONLY collected summaries.
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Model can be swapped via environment variable
# Default is a strong instruction-tuned LLM for long structured output
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
    """
    REPORT WRITER (EVIDENCE-GROUNDED)
    =================================

    Purpose
    -------
    Generates the final academic-style research report by:
        • Synthesizing across all summaries
        • Structuring content using predefined headings
        • Enforcing strict citation grounding

    This is the CORE synthesis stage of the system.

    Inputs
    ------
    title : str
        The report title generated earlier (query-aligned).

    headings : List[str]
        Ordered list of section headings, including:
            - Executive Summary
            - Topical sections
            - Conclusion
            - References

    summaries : Dict[str, str]
        Mapping of summary IDs → summary text.
        These are the ONLY factual sources allowed.

    references : List[str]
        Preformatted reference strings tied to summary IDs.

    Output
    ------
    str : Fully formatted report text following strict structure rules.

    Safety + Design Constraints
    ---------------------------
    • Prevents hallucinations by:
        - Forcing sentence-level citations
        - Banning external knowledge
    • Ensures reproducible structure
    • Keeps report traceable to evidence
    """

    # Build block of summaries for the model
    # Format: S1: <summary text>
    summary_block = "\n".join(
        f"{sid}: {text}"
        for sid, text in summaries.items()
    )

    # Headings are wrapped with markers so the model
    # must reproduce them EXACTLY in output
    heading_block = "\n".join(
        f"@@{h}@@" for h in headings
    )

    # Reference list block passed verbatim
    refs_block = "\n".join(references)

    # --------------------------------------------------
    # Highly Constrained Prompt
    # --------------------------------------------------
    # This prompt enforces:
    #   • Exact formatting
    #   • Citation-per-sentence
    #   • No markdown
    #   • No hallucinated facts
    #   • Section length expectations
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

    # LLM call to generate structured report
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # Low temp for consistency & factual discipline
        max_tokens=2500,  # Long output (full report)
    )

    # Return final report text
    return r.choices[0].message.content.strip()
