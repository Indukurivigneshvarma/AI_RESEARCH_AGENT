import os
import json
from typing import Dict, List
from openai import OpenAI


# --------------------------------------------------
# LLM Client Setup (Evaluation Model)
# --------------------------------------------------
# This evaluator uses a large instruction-following model
# hosted via OpenRouter. It acts as a *plan-aware grader*
# of the generated research report.

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv(
    "OPENROUTER_EVAL_MODEL",
    "meta-llama/llama-3.1-70b-instruct"
)


def _clean_llm_json(text: str) -> str:
    """
    Cleans LLM responses to extract valid JSON.

    Handles common formatting issues:
    - Markdown code blocks
    - Leading 'json' tags
    - Extra explanatory text before JSON
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

    first = text.find("{")
    if first != -1:
        text = text[first:]

    return text.strip()


def evaluate_report(
    user_query: str,
    research_plan: Dict[str, List[str]],
    report_text: str,
    summaries: Dict[str, str],
    headings: List[str],
    references: List[str],
) -> Dict:
    """
    REPORT EVALUATION ENGINE
    =========================

    Purpose
    -------
    Performs *automated quality assessment* of the final research report.

    This evaluator is:
        • Plan-aware  → checks coverage against intended dimensions
        • Evidence-grounded → checks claims against summaries only
        • Structure-aware → evaluates organization and clarity

    It does NOT:
        - Rewrite the report
        - Add corrections
        - Use outside knowledge

    It produces structured scoring across multiple dimensions.
    """

    # --------------------------------------------------
    # Format system inputs for the evaluator
    # --------------------------------------------------

    summary_block = "\n".join(
        f"{sid}: {text}"
        for sid, text in summaries.items()
    )

    heading_block = "\n".join(headings)
    refs_block = "\n".join(references)

    plan_block = "\n".join(
        f"- {d}"
        for d in research_plan.get("dimensions", [])
    )

    # --------------------------------------------------
    # Evaluation Prompt
    # --------------------------------------------------
    # The evaluator operates under strict instructions:
    # - Treat summaries as ground truth
    # - Treat research plan as intended scope
    # - Grade synthesis quality, not writing style alone

    prompt = f"""
You are a strict academic research evaluator.

YOUR TASK:
Evaluate the quality of the generated research report relative to the
USER'S RESEARCH QUESTION and the INTENDED RESEARCH PLAN.

You must assess ONLY what is provided.
Do NOT invent missing information.
Do NOT rewrite or fix the report.

================ EVALUATION PRINCIPLES ================

- The research plan defines the INTENDED SCOPE.
- The summaries define the ONLY allowed factual ground truth.
- The report must be evaluated based on how well it uses the summaries
  to fulfill the research plan.

================ EVALUATION CRITERIA ================

1. Accuracy & Grounding
2. Coverage & Completeness
3. Citation Quality
4. Structure & Clarity

================ OUTPUT RULES ================
- Return JSON ONLY
- No explanations
- No markdown
- No commentary

================ OUTPUT FORMAT ================
{{
  "overall_score": <float 0-10>,
  "accuracy": {{ "score": <0-10>, "notes": "<text>" }},
  "completeness": {{ "score": <0-10>, "notes": "<text>" }},
  "citation_quality": {{ "score": <0-10>, "notes": "<text>" }},
  "structure": {{ "score": <0-10>, "notes": "<text>" }},
  "limitations": [ "<limitation 1>", "<limitation 2>" ],
  "confidence_level": "low | medium | high"
}}

================ INPUTS ================

RESEARCH QUESTION:
{user_query}

RESEARCH PLAN (INTENDED SCOPE):
Goal:
{research_plan.get("goal")}

Planned Dimensions:
{plan_block}

HEADINGS:
{heading_block}

SUMMARIES (GROUND TRUTH):
{summary_block}

REFERENCES:
{refs_block}

GENERATED REPORT:
{report_text}

================ OUTPUT ================
Return ONLY the JSON object.
""".strip()

    # --------------------------------------------------
    # Run Evaluation LLM
    # --------------------------------------------------

    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=900,
    )

    raw = r.choices[0].message.content or ""
    cleaned = _clean_llm_json(raw)

    # --------------------------------------------------
    # Parse Evaluator Output
    # --------------------------------------------------
    # If parsing fails, return a structured failure object
    # instead of crashing the system.

    try:
        return json.loads(cleaned)
    except Exception:
        return {
            "status": "evaluation_failed",
            "reason": "Evaluator returned invalid JSON",
            "raw_output": raw.strip()[:1000],
        }
