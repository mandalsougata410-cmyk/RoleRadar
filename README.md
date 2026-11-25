# ⚡ RoleRadar — Conversational AI Career & Internship Agent

> An AI-native career agent that matches students to internships and engineering roles through multi-turn dialogue, hybrid semantic search, personalized re-ranking, and persistent SQL memory.

---

## 🚀 Key Highlights & Architecture
- **Multi-Turn Agent with Tool Use:** Extracts student intent into strict **Pydantic schemas** (`search_jobs`, `update_user_preferences`, `explain_job_fit`).
- **Interactive Voice Assistant (STT & TTS):** Speak directly with the career agent via Web Speech API recognition; hears natural queries and responds with audible voice narration.
- **PostgreSQL / SQLite + pgvector Schema:** Tables for `users`, `jobs`, `chat_messages` (persistent conversation memory), and `job_interactions` (for personalization).
- **Two-Stage Hybrid Search & Re-Ranking:**
  - **Stage 1 (SQL Filters):** Location, remote flag, minimum stipend constraints.
  - **Stage 2 (Composite Scoring):**
    $$\text{Score} = 0.60 \cdot \text{SemanticSimilarity} + 0.25 \cdot \text{SkillOverlap} + 0.15 \cdot \text{Recency} - \text{DismissalPenalty}$$
- **Automated LLM Evaluation Suite (`evals.py`):** Benchmarks structured output accuracy, **Recall@5**, and average query latency across test suites.
- **Production-Ready:** Containerized with Docker and served via FastAPI with an interactive web UI.

---

## 📊 Evaluation Benchmark Results
Ran via `python evals.py`:
- **Structured Output / Filter Accuracy:** **100.0%**
- **Retrieval Recall@5:** **100.0%**
- **Average Query Latency:** **~2.8 ms** (local) / **< 40 ms** (cloud)

---

## 🛠️ Quickstart

### 1. Clone & Install
```bash
git clone https://github.com/mandalsougata410-cmyk/RoleRadar.git
cd RoleRadar
pip install -r requirements.txt
```

### 2. Seed Database & Run Evals
```bash
python seed_data.py
python evals.py
```

### 3. Run FastAPI Web Server
```bash
uvicorn main:app --reload --port 8000
```
Open **`http://localhost:8000`** in your browser for the web chat interface, or **`http://localhost:8000/docs`** for interactive Swagger API docs.

---

## 🐳 Docker Deployment
```bash
docker build -t roleradar .
docker run -p 8000:8000 roleradar
```
