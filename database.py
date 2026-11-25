import os
import json
import sqlite3
import math
import tempfile
from typing import List, Dict, Any, Optional

# On Vercel serverless, ensure writable database in temp directory
if os.environ.get("VERCEL"):
    DB_FILE = os.path.join(tempfile.gettempdir(), "roleradar.db")
else:
    DB_FILE = os.path.join(os.path.dirname(__file__), "roleradar.db")

def get_db_connection():
    # check_same_thread=False allows FastAPI multi-threaded request workers
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        skills TEXT, -- JSON list
        preferred_locations TEXT, -- JSON list
        target_roles TEXT, -- JSON list
        min_stipend INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        is_remote INTEGER DEFAULT 0,
        stipend INTEGER DEFAULT 0,
        skills_required TEXT, -- JSON list
        requirements_text TEXT NOT NULL,
        embedding TEXT, -- JSON float list
        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        job_id INTEGER,
        action TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
