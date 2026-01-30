import json
import os

# FastAPI framework for building the web API
from fastapi import FastAPI

# Used to return HTML content (frontend UI)
from fastapi.responses import HTMLResponse

# Allows serving static files like generated PDFs
from fastapi.staticfiles import StaticFiles

# Used to validate incoming API request data
from pydantic import BaseModel

# Vector database client for persistent research memory
from src.vector_store.client import VectorStoreClient

# Main research pipeline controller
from src.controller.run import run_pipeline

# Object that logs every research step for transparency
from src.trace.research_trace import ResearchTrace


# ==========================================================
# FASTAPI APPLICATION INITIALIZATION
# ==========================================================
# This creates the web application instance.
# All API routes are attached to this app object.
app = FastAPI()

# Base directory of project (used to locate frontend file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------
# Serve generated files (like research PDFs)
# Any file saved in project root can be accessed via /files/
# Example: /files/report_1234.pdf
# ----------------------------------------------------------
app.mount("/files", StaticFiles(directory="."), name="files")


# ==========================================================
# PERSISTENT VECTOR STORE INITIALIZATION
# ==========================================================
# This database stores past research summaries as vectors,
# allowing future research to reuse knowledge instead of
# repeating web searches.
VECTOR_CLIENT = VectorStoreClient(embedding_dim=384)


# ==========================================================
# REQUEST DATA MODEL
# ==========================================================
# Defines structure of JSON body sent from frontend.
# Ensures API receives:
#   - query (research question)
#   - mode (quick / standard / deep)
class ResearchRequest(BaseModel):
    query: str
    mode: str


# ==========================================================
# HELPER FUNCTION — EXTRACT RESEARCH PLAN FROM TRACE
# ==========================================================
# The trace contains the full pipeline log.
# This function extracts only the RESEARCH PLAN section
# so it can be shown separately in the UI.
def extract_research_plan(trace_text: str) -> str:
    if not trace_text:
        return ""

    lines = trace_text.splitlines()
    plan_lines = []
    in_plan = False
    content_started = False

    for line in lines:
        # Detect beginning of research plan block
        if line.strip() == "RESEARCH PLAN":
            in_plan = True
            continue

        if in_plan:
            # Skip divider lines before content
            if line.strip().startswith("=") and not content_started:
                continue

            # Stop when next section begins
            if line.strip().startswith("=") and content_started:
                break

            if line.strip():
                content_started = True

            plan_lines.append(line)

    return "\n".join(plan_lines).strip()


# ==========================================================
# FRONTEND SERVING ROUTE
# ==========================================================
# When user visits the root URL ("/"), this serves the
# HTML user interface file.
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    # Reads frontend.html and returns it to browser
    with open(os.path.join(BASE_DIR, "src", "frontend.html"), "r", encoding="utf-8") as f:
        return f.read()


# ==========================================================
# MAIN RESEARCH API ENDPOINT
# ==========================================================
# Triggered when frontend presses "Run Research".
# It executes the entire research pipeline.
@app.post("/run")
def run_research(req: ResearchRequest):

    # Create trace logger to capture every step
    trace = ResearchTrace()

    # Execute full AI research pipeline
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

    # Format summaries for UI display
    summaries_text = ""
    if summaries:
        summaries_text = "\n\n".join(
            f"{s['id']} (score={s.get('total_score', 'NA')}):\n{s['summary']}"
            for s in summaries
        )

    # Extract structured research plan section
    plan_text = extract_research_plan(trace_text)

    # Convert evaluation JSON to readable string
    evaluation_text = ""
    if evaluation:
        try:
            evaluation_text = json.dumps(evaluation, indent=2)
        except Exception:
            evaluation_text = str(evaluation)

    # Send results back to frontend UI
    return {
        "summaries": summaries_text,
        "plan": plan_text,
        "trace": trace_text,
        "pdf": f"/files/{pdf_path}" if pdf_path else None,
        "evaluation": evaluation_text,
    }


# ==========================================================
# SERVER ENTRY POINT
# ==========================================================
# Allows running this file directly with:
# python src/main.py
# Useful for local testing and Hugging Face Spaces.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=7860)
