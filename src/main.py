import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.vector_store.client import VectorStoreClient
from src.controller.run import run_pipeline
from src.trace.research_trace import ResearchTrace


# ==========================================================
# FastAPI App
# ==========================================================
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Serve generated files (PDFs)
app.mount("/files", StaticFiles(directory="."), name="files")


# ==========================================================
# Persistent Vector Store
# ==========================================================
# ❗ FIXED: Removed invalid persist_dir argument
VECTOR_CLIENT = VectorStoreClient(embedding_dim=384)


# ==========================================================
# Request Model
# ==========================================================
class ResearchRequest(BaseModel):
    query: str
    mode: str


# ==========================================================
# Helper: Extract Research Plan
# ==========================================================
def extract_research_plan(trace_text: str) -> str:
    if not trace_text:
        return ""

    lines = trace_text.splitlines()
    plan_lines = []
    in_plan = False
    content_started = False

    for line in lines:
        if line.strip() == "RESEARCH PLAN":
            in_plan = True
            continue

        if in_plan:
            if line.strip().startswith("=") and not content_started:
                continue

            if line.strip().startswith("=") and content_started:
                break

            if line.strip():
                content_started = True

            plan_lines.append(line)

    return "\n".join(plan_lines).strip()


# ==========================================================
# Serve Frontend
# ==========================================================
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(os.path.join(BASE_DIR, "frontend.html"), "r", encoding="utf-8") as f:
        return f.read()


# ==========================================================
# Research API Endpoint
# ==========================================================
@app.post("/run")
def run_research(req: ResearchRequest):

    trace = ResearchTrace()

    (
        summaries,
        trace_text,
        report_text,
        pdf_path,
        evaluation,
    ) = run_pipeline(
        user_query=req.query,
        mode=req.mode,
        vector_client=VECTOR_CLIENT,
        trace=trace,
    )

    summaries_text = ""
    if summaries:
        summaries_text = "\n\n".join(
            f"{s['id']} (score={s.get('total_score', 'NA')}):\n{s['summary']}"
            for s in summaries
        )

    plan_text = extract_research_plan(trace_text)

    evaluation_text = ""
    if evaluation:
        try:
            evaluation_text = json.dumps(evaluation, indent=2)
        except Exception:
            evaluation_text = str(evaluation)

    return {
        "summaries": summaries_text,
        "plan": plan_text,
        "trace": trace_text,
        "pdf": f"/files/{pdf_path}" if pdf_path else None,
        "evaluation": evaluation_text,
    }


# ==========================================================
# Uvicorn Entry (HF + Local)
# ==========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=7860)
