import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from database import init_db, get_db_connection
from seed_data import seed_database
from models import ChatRequest, ChatResponse, InteractionRequest
from agent import handle_user_chat

app = FastAPI(
    title="RoleRadar API",
    description="Conversational AI Career & Internship Agent with Hybrid Search and Memory",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

# For serverless invocations where startup events might not fire eagerly
init_db()
seed_database()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "RoleRadar AI Agent"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    result = handle_user_chat(user_id=req.user_id, message=req.message)
    return ChatResponse(
        reply=result["reply"],
        tools_called=result["tools_called"],
        matched_jobs=result["matched_jobs"],
        user_profile=result["user_profile"]
    )

@app.post("/api/interaction")
def record_interaction(req: InteractionRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO job_interactions (user_id, job_id, action) VALUES (?, ?, ?)",
        (req.user_id, req.job_id, req.action)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "recorded": req.action}

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>RoleRadar API Running. Visit /docs for Swagger UI.</h1>"
