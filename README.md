---
title: AI Research Agent
emoji: 🧠
colorFrom: green
colorTo: white
sdk: docker
app_port: 7860
pinned: false
---

# 🧠 AI Research Agent

An AI-powered research system that automatically performs structured research and generates academic-style reports from a user’s question.

---

## 🚀 What It Does

Given a research question, the system:

1. Creates a research plan  
2. Searches and collects evidence from the web  
3. Summarizes sources using LLMs  
4. Stores knowledge in a vector database  
5. Detects agreement and conflicts between sources  
6. Resolves contradictions  
7. Generates a structured academic report  
8. Produces a downloadable PDF  
9. Evaluates report quality  

---

## 🏗 Main Components

- **Research Planner** – Understands the question and defines coverage
- **Query Generator** – Creates structured search queries
- **Web Retrieval** – Collects sources from the internet
- **Summarizer** – Produces dense research summaries
- **Vector Store** – Persistent memory for past research
- **Agreement & Conflict Analysis** – Cross-source validation
- **Report Writer** – Generates the final academic report
- **PDF Generator** – Formats report into PDF
- **Evaluator** – Scores report quality

---

## 🧠 Models Used

The system uses multiple LLM providers:

- Groq (LLaMA models)
- OpenRouter
- Cohere
- Google Gemini

---

## ⚙️ Run Locally

### 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
