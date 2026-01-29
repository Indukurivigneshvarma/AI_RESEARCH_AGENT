---
title: AI Research Agent
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# AI Research Agent

Multi model research automation system

Employee Name: <I. Vignesh Varma>

---

## 1. Research Question / Problem Statement

Large Language Models (LLMs) can generate fluent answers to complex questions, but they do not inherently perform structured research. A single prompt typically produces responses that are:

- Based on limited internal knowledge  
- Prone to hallucinations  
- Not grounded in multiple independent sources  
- Lacking cross-source validation or contradiction handling  

This project addresses the following core research problem:

> **How can an AI system autonomously conduct structured, multi-source research, validate cross-source agreement, detect factual conflicts, and synthesize a grounded academic-style report with explicit evidence tracking?**

The goal is not simple text generation, but the design of a reasoning pipeline that mimics a disciplined research process:

**planning → retrieval → summarization → evidence comparison → synthesis → evaluation**

---

## 2. Motivation & Relevance

Modern LLM usage often treats the model as a direct answer engine. However, in real research and decision-making scenarios, reliability depends on:

- Consulting multiple sources  
- Weighing source credibility  
- Identifying agreement patterns  
- Detecting contradictions  
- Synthesizing findings in a structured manner  

Standard prompting does not enforce these steps, which leads to:

- Unverified claims  
- Hidden conflicts between sources  
- Lack of traceability  
- Overconfident but weakly grounded outputs  

This project is motivated by the need for LLM systems that behave less like chatbots and more like research assistants.

The AI Research Agent introduces a modular, multi-stage architecture where LLMs are used as components within a controlled pipeline rather than as a single monolithic reasoner. The system integrates:

- Structured research planning  
- Web-based evidence collection  
- Dense evidence summarization  
- Persistent vector memory  
- Cross-source agreement and conflict reasoning  
- Evidence-grounded report generation  
- Automated quality evaluation  

This approach is relevant to domains such as:

- Policy research  
- Technical analysis  
- Literature reviews  
- Risk assessment  
- Decision-support systems  

where evidence grounding and reasoning transparency are more important than fluent text generation alone.

---

## 3. System Architecture

The AI Research Agent is designed as a **multi-stage research reasoning system** where Large Language Models operate as controlled components inside a structured pipeline rather than as a single end-to-end generator.

The system follows a disciplined research workflow:

> **Planning → Iterative Discovery → Evidence Validation → Synthesis → Evaluation**

---

### 🔷 High-Level Architecture Diagram


---

## 🔍 Architectural Overview

The system consists of **five major subsystems**:

1. **Research Planning Layer**  
2. **Iterative Discovery Loop**  
3. **Post-Discovery Evidence Validation**  
4. **Report Engine**  
5. **Evaluation Layer**

Each subsystem performs a **distinct cognitive function** in the automated research process.

---

## 3.1 Research Planning Layer

This layer transforms the raw user question into a **structured research scope** before any retrieval occurs.

| Component | Model | Function |
|-----------|-------|----------|
| **Research Plan Generator** | Cohere `command-a-03-2025` | Produces structured research dimensions |
| **Initial Subquery Generator** | Groq `llama-3.1-8b-instant` | Generates broad coverage-oriented search queries |

**Purpose:**  
The system first defines *what must be researched*, enforcing structured reasoning before evidence collection begins.

---

## 3.2 Iterative Discovery Loop

This is the **core exploration engine**. It runs for each generated subquery.

### Step A — Embedding + Vector Search  
The subquery is embedded and matched against **stored query memory** to retrieve semantically similar past research.

### Step B — Cross-Encoder Rerank  
A cross-encoder improves semantic precision by re-ranking retrieved candidates.

### Step C — Intent Selection LLM  
Groq **LLaMA 3.3-70B** determines whether any stored query matches the *same research intent*.

This produces a **decision branch**:

| Path | Description |
|------|-------------|
| **Reuse Summary + Metadata** | Previously stored evidence is reused |
| **Web Discovery** | New evidence is collected from the web |

---

### If Web Discovery is triggered:

1. **Tavily Search** retrieves candidate sources  
2. **Content Extraction** using Newspaper3k  
3. **Summary Generation** using LLaMA models  
4. **Credibility Scoring** assigns trust weight  
5. **Vector Store Upsert** stores the summary (URL deduplication enforced)

All evidence converges into:

### **Collected Summaries**

This forms the evidence pool for the current iteration.

---

## 3.3 Coverage Refinement

After each discovery round, the system evaluates research coverage.

| Mode | Refinement Loops |
|------|------------------|
| **Quick** | No refinement |
| **Standard** | 1 refinement loop |
| **Deep** | 2 refinement loops |

Cohere generates **new targeted subqueries** to fill coverage gaps.  
The system then loops back into the discovery process.

---

## 3.4 Post-Discovery Evidence Validation

Once sufficient summaries are collected, the system performs structured cross-source reasoning.

| Stage | Model | Purpose |
|-------|-------|---------|
| **Agreement Detection** | Gemini Flash | Finds cross-source support patterns |
| **Agreement Scoring** | Rule-based + LLM | Combines credibility + agreement strength |
| **Conflict Detection** | Gemini Flash | Identifies hard factual contradictions |
| **Conflict Resolution Engine** | LLM-guided | Higher-scoring evidence wins; weaker claims are rewritten |

This produces:

### **Final Trust-Weighted Summaries**

---

## 3.5 Report Engine

Validated evidence is converted into an academic-style research report.

| Component | Model | Role |
|-----------|-------|------|
| Citation Mapping | Rule-based | Links claims to sources |
| Title & Headings Generation | Groq LLaMA 3.3-70B | Report structure |
| Report Writing | OpenRouter LLaMA 3.1-70B | Evidence-grounded synthesis |
| PDF Generation | ReportLab | Final document output |

The system enforces:

- Sectioned structure  
- Sentence-level citations  
- No unsupported claims  

---

## 3.6 Evaluation Layer

The final report undergoes **plan-aware evaluation**.

| Component | Model | Purpose |
|-----------|-------|---------|
| Plan-Aware Report Evaluation | LLaMA 3.1-70B | Scores report quality vs research plan |

This ensures the system is evaluated as a **research reasoning pipeline**, not a simple text generator.

---

## 🎯 Architectural Significance

This system differs from standard LLM applications because it:

- Uses LLMs as **components**, not as the whole system  
- Performs **iterative coverage refinement**  
- Implements **cross-source validation**  
- Handles **conflict resolution explicitly**  
- Maintains **persistent research memory**  
- Enforces **citation-constrained synthesis**

The architecture therefore represents a **research automation engine**, not a single-shot generation model.

---

## 4. Models Used

This system deliberately uses different models for different cognitive roles rather than relying on a single large model.  
It combines **LLMs for reasoning** with **specialized embedding and ranking models for retrieval**, forming a hybrid research architecture.

Each model is chosen based on task type, reasoning requirement, latency, and cost-efficiency.

| System Stage | Provider / Type | Model | Role in Pipeline | Why This Model |
|--------------|------------------|-------|------------------|----------------|
| **Research Plan Generation** | Cohere (LLM) | command-a-03-2025 | Produces structured research dimensions | Strong structured reasoning and decomposition capability |
| **Initial Subquery Generation** | Groq (LLM) | llama-3.1-8b-instant | Generates broad coverage search queries | Fast, cost-efficient, good semantic breadth |
| **Intent Selection** | Groq (LLM) | llama-3.3-70b-versatile | Determines whether a stored query matches current intent | Requires nuanced semantic equivalence reasoning |
| **Summary Generation (Provider 1)** | Groq (LLM) | llama-3.1-8b-instant | Produces dense factual summaries | Low latency, used for half of ingestion load |
| **Summary Generation (Provider 2)** | OpenRouter (LLM) | llama-3.1-8b-instruct | Alternate summarizer for diversity and provider balancing | Adds model variance and resilience |
| **Coverage Refinement** | Cohere (LLM) | command-a-03-2025 | Identifies missing research dimensions | Good at structured gap analysis |
| **Agreement Detection** | Google AI Studio (LLM) | gemini-flash-latest | Detects cross-source support relations | Efficient pairwise reasoning over multiple texts |
| **Conflict Detection** | Google AI Studio (LLM) | gemini-flash-latest | Detects hard factual contradictions | Good instruction following for strict logical rules |
| **Summary Rewriting** | Groq (LLM) | llama-3.1-8b-instant | Removes losing claims after conflict resolution | Fast controlled rewriting |
| **Title & Headings Generation** | Groq (LLM) | llama-3.3-70b-versatile | Generates report structure | Requires high-level abstraction |
| **Report Writing** | OpenRouter (LLM) | llama-3.1-70b-instruct | Synthesizes academic report | Strong long-form synthesis and instruction adherence |
| **Evaluation** | OpenRouter (LLM) | llama-3.1-70b-instruct | Plan-aware quality assessment | Capable of multi-criteria evaluation |
| **Query Embedding Model** | Sentence-Transformers | all-MiniLM-L6-v2 | Converts queries into dense vectors for vector search | Lightweight, fast, and strong semantic retrieval performance |
| **Cross-Encoder Reranker** | Sentence-Transformers | cross-encoder/ms-marco-MiniLM-L-6-v2 | Reranks vector search results using deep pairwise scoring | Improves semantic precision beyond bi-encoder retrieval |

---

### Model Strategy Rationale

Instead of scaling model size everywhere, the system follows a **specialized model orchestration approach**:

**Small fast models →** retrieval, summarization, rewriting  
**Structured reasoning models →** planning and coverage analysis  
**Large synthesis models →** report writing and evaluation  
**IR models (embeddings + cross-encoders) →** semantic retrieval and ranking  

This results in:

- Lower latency during discovery  
- Better cost control  
- Task-appropriate reasoning depth  
- Stronger retrieval precision  
- Reduced hallucination risk through evidence-grounded synthesis

---

## 5. Prompting Strategy

Prompting in this system is not generic.  
Each LLM stage is governed by task-specific prompt constraints designed to control behavior and reduce hallucination.

---

### 5.1 Planning Prompts

Used for research plan and coverage refinement.

**Design principles:**

- Force structured outputs (JSON)  
- Explicitly forbid explanations  
- Separate “dimensions” from search queries  
- Prevent scope expansion  

**Goal:** Convert a vague research question into a formal coverage blueprint.

---

### 5.2 Retrieval-Oriented Prompts

Used for:

- Subquery generation  
- Intent selection  

**Key constraints:**

- Must stay grounded in the research goal  
- Cannot introduce new scope  
- Must treat candidate queries as literal questions  
- Strict semantic equivalence rules  

**Goal:** Prevent semantic drift and irrelevant reuse.

---

### 5.3 Summary Generation Prompts

These are highly constrained to reduce hallucination.

**Rules enforced:**

- Single-paragraph output  
- Extract only from provided text  
- No meta commentary  
- Include all quantitative data if present  
- Explicitly state absence of numbers if missing  

**Goal:** Maximize factual recall while preventing fabrication.

---

### 5.4 Cross-Source Reasoning Prompts

Used in agreement and conflict detection.

**Agreement detection prompt:**

- Allows only predefined relation labels  
- Requires pairwise analysis  

**Conflict detection prompt:**

- Defines strict logical contradiction criteria  
- Disallows marking conflicts for differences in framing or scope  
- Forces internal logical impossibility test  

**Goal:** Ensure evidence comparison is rule-based, not heuristic.

---

### 5.5 Rewriting Prompts

Used only after conflict resolution.

**Rules:**

- Remove only specified claims  
- Preserve tone and all other content  
- No summarization or additions  

**Goal:** Surgical correction instead of regeneration.

---

### 5.6 Report Writing Prompts

The report writer operates under format and citation constraints:

- Must use predefined headings  
- Sentence-level citations mandatory  
- No uncited factual claims  
- No external knowledge allowed  

**Goal:** Turn summaries into a traceable academic synthesis.

---

### 5.7 Evaluation Prompts

The evaluator is instructed to:

- Use summaries as ground truth  
- Compare report against research plan  
- Score across multiple dimensions  
- Output structured JSON only  

**Goal:** Automated but plan-aware quality control.

---

### Prompting Philosophy

The system uses constraint-driven prompting rather than creative prompting.

This approach:

- Reduces hallucinations  
- Enforces structure  
- Enables deterministic system behavior  
- Makes outputs auditable  

---

## 6. Evaluation Protocol

The system is evaluated as a research synthesis engine, not merely as a text generator.  
Evaluation focuses on whether the system produces grounded, complete, and structured research outputs aligned with the research plan.

---

### 6.1 Evaluation Philosophy

The evaluation framework is plan-aware and evidence-grounded:

- The research plan defines intended scope  
- The collected summaries define allowed factual ground truth  
- The report must synthesize only from those summaries  

This prevents:

- Hallucinated facts  
- Scope drift  
- Unstructured narrative generation  

---

### 6.2 Evaluation Dimensions

Each generated report is automatically evaluated using an LLM-based evaluator under strict instructions.  
The evaluation produces structured scores across the following criteria:

#### 1. Accuracy & Grounding

Measures whether the report:

- Contains only claims supported by collected summaries  
- Avoids unsupported or fabricated statements  
- Maintains factual consistency  

Failure examples:

- Introducing data not present in summaries  
- Overstating weak evidence  

---

#### 2. Coverage & Completeness

Measures alignment with the research plan:

- Are all planned research dimensions addressed?  
- Are any dimensions missing or weakly covered?  
- Does the synthesis fulfill the research goal?  

This evaluates the effectiveness of the discovery engine, not just writing quality.

---

#### 3. Citation Quality

The report must:

- Cite every declarative sentence  
- Use sentence-level citation markers  
- Reference only the generated summary IDs  

This ensures traceability from report → summaries → sources.

---

#### 4. Structure & Clarity

Evaluates:

- Logical section organization  
- Coherence between sections  
- Proper use of the structured report format  
- Balanced treatment of topics  

---

### 6.3 Modes Compared

The system includes three discovery modes:

| Mode | Iterations | Purpose |
|------|-----------|---------|
| Quick | Initial subqueries only | Fast exploratory research |
| Standard | 1 refinement loop | Balanced depth and cost |
| Deep | 2 refinement loops | Maximum coverage and robustness |

Experiments (see experiments/) compare Standard vs Deep mode to measure:

- Increase in coverage score  
- Change in agreement scores  
- Reduction in conflicts  
- Impact on evaluation scores  

---

### 6.4 Experimental Setup

Each experiment file specifies:

- Mode (standard / deep)  
- Number of discovery iterations  
- Retrieval depth  
- Random seed  

The evaluation notebook runs multiple research questions under each mode and logs:

- Number of summaries collected  
- Average credibility score  
- Agreement score distribution  
- Conflict counts  
- Final evaluation scores  

This allows analysis of how iterative coverage refinement impacts research quality.

---

### 6.5 Why LLM-Based Evaluation?

The evaluator is used because:

- The task involves semantic synthesis, not classification  
- Manual grading is not scalable  
- The evaluator is constrained to use only system outputs  

Thus, evaluation remains automated yet grounded.

---

## 7. Key Results

This section summarizes observed system behavior across experiments.

---

### 7.1 Iterative Discovery Improves Coverage

Comparing Standard vs Deep mode shows:

- More research dimensions addressed  
- Fewer weak or underdeveloped sections  
- Higher completeness scores  

The coverage refinement loop helps the system:

- Identify missing conceptual angles  
- Generate targeted follow-up queries  

This demonstrates that iterative reasoning improves research synthesis.

---

### 7.2 Agreement Scoring Improves Evidence Reliability

The agreement detector identifies cross-source support relationships.  
Summaries supported by multiple sources receive higher total scores.

Effects observed:

- Stronger summaries dominate conflict resolution  
- Weak or isolated claims are down-weighted  
- Final reports emphasize well-supported findings  

This produces trust-weighted synthesis, not equal-weight aggregation.

---

### 7.3 Conflict Resolution Reduces Contradictions

Conflict detection isolates hard factual contradictions.  
Lower-scoring summaries have conflicting claims removed via controlled rewriting.

Outcomes:

- Reports contain fewer logical inconsistencies  
- Evidence alignment improves  
- Evaluation accuracy scores increase  

This shows the system performs evidence arbitration, not blind merging.

---

### 7.4 Multi-Model Orchestration is Effective

Using specialized models for different roles resulted in:

- Faster discovery stage (small models)  
- Stronger synthesis and evaluation (large models)  
- Balanced cost-performance tradeoff  

This validates the task-specialized model orchestration approach.

---

### 7.5 Citation-Constrained Writing Reduces Hallucination

By forcing sentence-level citations:

- Unsupported claims are minimized  
- Report traceability is improved  
- Evaluation accuracy scores remain stable across runs  

The system behaves more like a research compiler than a chatbot.

---

### 7.6 Overall System Behavior

The system consistently:

- Produces structured academic reports  
- Grounds synthesis in collected evidence  
- Improves quality through iterative refinement  
- Resolves cross-source contradictions  

This demonstrates a full research automation pipeline, not just LLM text generation.

---

## 8. Known Limitations & Ethical Considerations

Despite the system’s structured design and safeguards, it has important limitations.

---

### 8.1 Technical Limitations

#### 1. Dependence on Web Source Quality

The system’s knowledge comes from web-retrieved sources. If:

- Sources are low-quality  
- Metadata is incomplete  
- Information is outdated  

then the summaries and final report may reflect those weaknesses.

The system can weight evidence, but it cannot guarantee correctness beyond available sources.

---

#### 2. LLM-Based Reasoning Is Probabilistic

Agreement detection, conflict detection, and evaluation rely on LLM judgments. While prompts are highly constrained:

- Edge-case reasoning errors may occur  
- Subtle contradictions may be missed  
- Semantic nuances may be misinterpreted  

This means the system provides automated research assistance, not verified truth.

---

#### 3. Vector Memory Bias

Previously stored summaries can be reused. This improves efficiency but may introduce:

- Reinforcement of earlier evidence patterns  
- Reduced diversity of perspectives  
- Potential over-representation of earlier topics  

The intent selection step mitigates this but does not fully eliminate the risk.

---

#### 4. Scope Limited by Query Formulation

The system assumes the user provides a clear research question. Ambiguous or poorly defined queries can lead to:

- Suboptimal research plans  
- Misaligned discovery  
- Reduced coverage quality  

The system does not perform deep semantic disambiguation of user intent.

---

#### 5. Evaluation Is Model-Based

The evaluator is itself an LLM. While constrained to system outputs:

- Scores may vary slightly across runs  
- Evaluation reflects structured judgment, not human peer review  

Thus, evaluation should be interpreted as system-level quality signals, not definitive grading.

---

### 8.2 Ethical Considerations

#### 1. No Sensitive or Private Data

The system only processes:

- Public web content  
- Synthetic or project-defined data  

No personal, private, or proprietary data is used.

---

#### 2. Risk of Misinformation Propagation

Because the system synthesizes from online sources, there is a risk of:

- Propagating incorrect claims present in sources  
- Giving structure and authority to weak evidence  

Mitigations include:

- Credibility scoring  
- Cross-source agreement weighting  
- Conflict detection  

But users must treat outputs as assisted research, not authoritative truth.

---

#### 3. Automation of Research Does Not Replace Expertise

The system automates:

- Information gathering  
- Summarization  
- Structural synthesis  

However, it does not replace:

- Domain expertise  
- Critical interpretation  
- Peer validation  

Human oversight remains necessary.

---

#### 4. Transparency & Traceability

Every statement in the report is citation-linked to summaries and sources.  
This improves accountability and allows users to verify claims independently.

---

#### 5. Use of Generative AI

Generative models were used for:

- Code generation assistance  
- Prompt drafting  
- Report synthesis  
- Evaluation automation  

All model roles and usage are documented for transparency.

---

## 9. Reproducibility Instructions

This section explains how another engineer can reproduce system behavior.

---

### 9.1 Hardware Assumptions

- No GPU required  
- Runs on standard CPU environment  
- Tested on local machine and cloud container environments  

Memory usage depends on:

- Embedding model (MiniLM)  
- FAISS vector store size  

---

### 9.2 Environment Setup

- Clone repository  
- Create Python virtual environment  
- Install dependencies from requirements.txt  
- Add API keys using .env.example template  
- Run FastAPI app or notebooks  

---

### 9.3 Runtime Characteristics

Approximate runtime per query:

| Mode | Time |
|------|------|
| Quick | Fastest |
| Standard | Moderate |
| Deep | Longest |

Time depends on:

- Number of web calls  
- LLM response times  
- Number of iterations  

---

### 9.4 Randomness & Determinism

Sources of nondeterminism:

- LLM sampling (even at low temperature)  
- Web content variability  
- Search engine result differences  

Mitigations:

- Low temperature settings  
- Fixed experiment configurations  
- Structured prompts  

Exact bitwise reproducibility is not guaranteed, but behavioral reproducibility is expected.

---

### 9.5 API & Cost Considerations

The system uses multiple API providers. Costs depend on:

- Number of discovery iterations  
- Number of summaries generated  
- Report length  
- Evaluation calls  

Deep mode consumes more API usage due to extra iterations.

---

### 9.6 Experiment Reproduction

To reproduce experiments:

- Use experiment YAML files  
- Run evaluation notebook  

Compare:

- Coverage scores  
- Agreement scores  
- Evaluation results  

These correspond to the reported findings.

---

### 9.7 Version Control

All:

- Model names  
- System parameters  
- Experiment settings  

are explicitly defined in:

- project.yaml  
- experiments/  
- src/config.py  

This ensures configuration traceability.


