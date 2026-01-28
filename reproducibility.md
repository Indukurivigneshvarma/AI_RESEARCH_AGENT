# Reproducibility Statement

This document defines the conditions required to reproduce the behavior of the **AI Research Agent** system. Because the system integrates probabilistic large language models (LLMs) and live web data, **exact text outputs are not guaranteed**, but the **pipeline behavior, research logic, and system decisions** are reproducible within the constraints described below.

---

## 1. Hardware Assumptions

This project is designed to run **without a GPU**.

**Minimum environment:**
- CPU-only system  
- 8 GB RAM recommended  
- Stable internet connection required  

All heavy computation is handled by external APIs:
- LLM reasoning → Groq, OpenRouter, Cohere, Gemini  
- Web search and extraction → Tavily  

Local compute is only used for:
- FAISS vector similarity search  
- SentenceTransformer embeddings (MiniLM CPU model)  
- Orchestration and PDF generation  

This makes the system deployable on laptops, cloud VMs, and lightweight servers.

---

## 2. Runtime Estimates

Runtime depends on research depth (mode):

| Mode     | Iterations | Typical Runtime |
|----------|-----------|-----------------|
| Quick    | 1         | 20–60 sec       |
| Standard | 2         | 40–80 sec       |
| Deep     | 3         | 60–150 sec      |

Runtime varies due to:
- Web latency  
- API response speed  
- Report length  

---

## 3. Random Seed Handling

The system reduces randomness where possible:

- LLM temperature is set **low (0.0–0.3)** for planning, writing, and analysis.
- FAISS retrieval and cross-encoder reranking are deterministic given identical inputs.
- No stochastic sampling is used in vector similarity.

Full determinism is not possible due to probabilistic LLM APIs and dynamic web content.

---

## 4. Known Sources of Nondeterminism

### LLM Variability  
LLM providers may produce slightly different wording even with low temperature.

### Web Search Changes  
Search rankings and available articles change over time.

### Content Drift  
Web pages may be updated after ingestion.

### Model Updates  
Providers may update models without notice.

### Vector Similarity Ties  
Near-identical embedding scores may change ranking order in rare cases.

---

## 5. Cost Considerations

Primary cost drivers:

- Tavily search and extraction  
- Groq summarization  
- Cohere planning and refinement  
- OpenRouter long-form report writing  
- Gemini agreement and conflict detection  

| Mode     | Relative API Cost |
|----------|-------------------|
| Quick    | Low               |
| Standard | Medium            |
| Deep     | High              |

No GPU costs are incurred locally.

---

## 6. Data Dependencies

- Credibility datasets must exist in `data/credibility/`  
- Only publicly available web data is used  
- No private or sensitive data is involved  

---

## 7. Deterministic vs Probabilistic Components

**Deterministic**
- Credibility scoring  
- Agreement scoring weights  
- Conflict resolution logic  
- PDF rendering  
- Trace logging  

**Probabilistic**
- Research planning  
- Query refinement  
- Summary generation  
- Agreement detection  
- Conflict detection
- Report synthesis  
- Evaluation scoring  

---

## 8. Reproducibility Guarantee

When run with:
- Same code version  
- Same environment variables  
- Same credibility datasets  
- Similar time window (web stable)  

Then:

- The same pipeline stages execute  
- Similar sources are selected  
- Similar research conclusions emerge  
- The research process remains structurally consistent  

Exact sentences may vary, but reasoning flow and evidence structure remain stable.

---

