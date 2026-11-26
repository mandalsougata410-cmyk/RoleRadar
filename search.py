import json
import sqlite3
from typing import List, Dict, Any, Optional
from database import get_db_connection, cosine_similarity

def search_and_rank_jobs(
    user_id: str,
    query_embedding: Optional[List[float]] = None,
    target_role: Optional[str] = None,
    location: Optional[str] = None,
    remote_only: Optional[bool] = None,
    min_stipend: Optional[int] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Two-Stage Hybrid Search & Personalized Re-Ranking:
    Stage 1: Hard SQL metadata filtering
    Stage 2: Score = 0.60 * semantic_similarity + 0.25 * skill_overlap + 0.15 * recency_boost (minus dismissed jobs)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch user preferences & interaction history
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_skills = set(json.loads(user_row["skills"])) if user_row and user_row["skills"] else set()
    
    cursor.execute("SELECT job_id, action FROM job_interactions WHERE user_id = ?", (user_id,))
    interactions = cursor.fetchall()
    dismissed_ids = {row["job_id"] for row in interactions if row["action"] == "dismissed"}
    saved_ids = {row["job_id"] for row in interactions if row["action"] == "saved"}
    
    # Stage 1: SQL Filtering
    query = "SELECT * FROM jobs WHERE is_active = 1"
    params = []
    
    if remote_only is True:
        query += " AND is_remote = 1"
    if min_stipend and min_stipend > 0:
        query += " AND stipend >= ?"
        params.append(min_stipend)
    if location and location.lower() != "any":
        query += " AND (LOWER(location) LIKE ? OR is_remote = 1)"
        params.append(f"%{location.lower()}%")
    if target_role:
        query += " AND (LOWER(title) LIKE ? OR LOWER(requirements_text) LIKE ?)"
        params.extend([f"%{target_role.lower()}%", f"%{target_role.lower()}%"])
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    candidates = []
    for r in rows:
        job_id = r["id"]
        # Skip dismissed jobs
        if job_id in dismissed_ids:
            continue
            
        skills_req = set(json.loads(r["skills_required"])) if r["skills_required"] else set()
        
        # 1. Semantic similarity
        sem_score = 0.5
        if query_embedding and r["embedding"]:
            job_emb = json.loads(r["embedding"])
            sem_score = max(0.0, cosine_similarity(query_embedding, job_emb))
            
        # 2. Skill overlap score (Jaccard / intersection)
        if skills_req and user_skills:
            overlap = len(skills_req.intersection(user_skills)) / len(skills_req)
        else:
            overlap = 0.5
            
        # 3. Recency / Saved Boost
        recency_score = 0.8
        if job_id in saved_ids:
            recency_score = 1.0
            
        final_score = (0.60 * sem_score) + (0.25 * overlap) + (0.15 * recency_score)
        
        candidates.append({
            "id": r["id"],
            "title": r["title"],
            "company": r["company"],
            "location": r["location"],
            "is_remote": bool(r["is_remote"]),
            "stipend": r["stipend"],
            "skills_required": list(skills_req),
            "requirements_text": r["requirements_text"],
            "about_company": r["about_company"] if "about_company" in r.keys() and r["about_company"] else "",
            "score": round(final_score, 3),
            "match_pct": int(final_score * 100)
        })
        
    conn.close()
    
    # Rank descending by composite score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:limit]

def get_job_details(job_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)
