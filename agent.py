import os
import json
import re
from typing import Dict, Any, List, Tuple
from database import get_db_connection
from search import search_and_rank_jobs, get_job_details
from models import UserIntentFilter

# System prompt defining tools and persona
SYSTEM_PROMPT = """You are RoleRadar, an expert AI Career and Internship Agent.
Your goal is to help students discover and match with the best software engineering and AI internships.

You have access to 3 tools:
1. `search_jobs(role, skills, location, remote_only, min_stipend)`: Searches the internship index.
2. `update_user_preferences(skills, target_roles, location, min_stipend)`: Saves updated user preferences to database.
3. `explain_job_fit(job_id)`: Explains why a candidate matches or has skill gaps for a job.

When speaking with the user, maintain persistent context, be direct and encouraging, and explain match scores clearly.
"""

def extract_filters_rule_based(message: str) -> UserIntentFilter:
    """
    Structured extraction parsing intent, skills, location, remote, stipend, and role.
    """
    text = message.lower()
    
    # Skills extraction
    known_skills = ["python", "fastapi", "sql", "postgresql", "docker", "react", "node.js", "pytorch", "aws", "llm", "go"]
    found_skills = [s.capitalize() if s != "node.js" else "Node.js" for s in known_skills if re.search(rf"\b{re.escape(s)}\b", text)]
    
    # Remote detection
    remote_only = True if "remote" in text or "wfh" in text else None
    
    # Location
    location = None
    for city in ["bengaluru", "bangalore", "gurugram", "gurgaon", "mumbai", "delhi", "hyderabad", "pune"]:
        if city in text:
            location = "Bengaluru" if "bang" in city else ("Gurugram" if "gur" in city else city.capitalize())
            break
            
    # Stipend extraction
    min_stipend = None
    stipend_match = re.search(r"(\d+)\s*(k|thousand|000)", text)
    if stipend_match:
        val = int(stipend_match.group(1))
        unit = stipend_match.group(2)
        min_stipend = val * 1000 if unit in ["k", "thousand"] else val
    else:
        num_match = re.search(r"(?:stipend|paying|above|min)\s*(\d{4,6})", text)
        if num_match:
            min_stipend = int(num_match.group(1))
            
    # Role detection
    role = None
    if "backend" in text:
        role = "Backend"
    elif "ai" in text or "llm" in text or "ml" in text:
        role = "AI"
    elif "full stack" in text or "fullstack" in text:
        role = "Full Stack"
    elif "frontend" in text:
        role = "Frontend"
    elif "devops" in text or "cloud" in text:
        role = "DevOps"
        
    return UserIntentFilter(
        role=role,
        skills=found_skills,
        location=location,
        remote_only=remote_only,
        min_stipend=min_stipend
    )

def handle_user_chat(user_id: str, message: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Store incoming message in persistent chat memory
    cursor.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (user_id, message))
    
    # 2. Extract structured intent & filters
    filters = extract_filters_rule_based(message)
    tools_called = []
    
    # 3. Check if user wants to update their profile
    if filters.skills or filters.min_stipend or filters.location:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        current_skills = json.loads(user["skills"]) if user and user["skills"] else []
        new_skills = list(set(current_skills + filters.skills))
        
        cursor.execute("""
        UPDATE users 
        SET skills = ?, 
            preferred_locations = CASE WHEN ? IS NOT NULL THEN json_array(?) ELSE preferred_locations END,
            min_stipend = COALESCE(?, min_stipend),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (json.dumps(new_skills), filters.location, filters.location, filters.min_stipend, user_id))
        tools_called.append("update_user_preferences")
        
    # 4. Search and rank jobs
    tools_called.append("search_jobs")
    matched_jobs = search_and_rank_jobs(
        user_id=user_id,
        target_role=filters.role,
        location=filters.location,
        remote_only=filters.remote_only,
        min_stipend=filters.min_stipend,
        limit=4
    )
    
    # 5. Formulate natural response
    if matched_jobs:
        top_job = matched_jobs[0]
        reply_parts = [
            f"I found {len(matched_jobs)} top opportunities matching your profile:",
            f"\n🔥 **Top Pick: {top_job['title']} at {top_job['company']}** ({top_job['location']})",
            f"• **Stipend:** ₹{top_job['stipend']:,}/month",
            f"• **Match Score:** {top_job['match_pct']}% based on your skills ({', '.join(top_job['skills_required'])})",
            f"• **Requirements:** {top_job['requirements_text'][:120]}...\n",
            "You can save or dismiss any of these cards, or tell me to refine by tech stack, stipend, or location!"
        ]
        reply = "\n".join(reply_parts)
    else:
        reply = "I couldn't find an exact match for those specific filters. Would you like to expand your location or stipend preferences?"
        
    # 6. Store assistant response
    cursor.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'assistant', ?)", (user_id, reply))
    conn.commit()
    
    # Fetch updated user profile
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    updated_user = dict(cursor.fetchone() or {})
    if updated_user.get("skills"):
        updated_user["skills"] = json.loads(updated_user["skills"])
    conn.close()
    
    return {
        "reply": reply,
        "tools_called": tools_called,
        "matched_jobs": matched_jobs,
        "user_profile": updated_user
    }
