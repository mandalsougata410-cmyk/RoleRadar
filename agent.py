import os
import json
import re
from typing import Dict, Any, List
from database import get_db_connection
from search import search_and_rank_jobs, get_job_details
from models import UserIntentFilter

def parse_user_intent_dynamic(message: str) -> UserIntentFilter:
    """
    Intelligent dynamic intent parser that handles ANY query, question, or comment:
    - Greetings & general chit-chat ("hi", "who are you?", "help me")
    - Broad questions ("what jobs do you have?", "recommend something good")
    - Custom constraints (stipend, remote/hybrid, any city/location, technical or non-technical skills)
    - Profile updates ("I know Java and C++", "I want 40k")
    """
    text = message.lower().strip()
    
    # 1. Comprehensive Tech & Industry Skill Dictionary
    SKILL_MAP = {
        "python": "Python", "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
        "sql": "SQL", "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "mysql": "MySQL",
        "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
        "react": "React", "nextjs": "Next.js", "next.js": "Next.js", "node": "Node.js", "node.js": "Node.js",
        "typescript": "TypeScript", "javascript": "JavaScript", "js": "JavaScript", "ts": "TypeScript",
        "pytorch": "PyTorch", "tensorflow": "TensorFlow", "keras": "Keras",
        "llm": "LLMs", "llms": "LLMs", "ai": "AI", "ml": "Machine Learning", "nlp": "NLP",
        "rag": "RAG", "embeddings": "Embeddings", "vector": "Vector DB",
        "aws": "AWS", "gcp": "GCP", "azure": "Azure", "cloud": "Cloud",
        "java": "Java", "spring": "Spring Boot", "golang": "Go", "go": "Go", "c++": "C++", "rust": "Rust",
        "kafka": "Kafka", "redis": "Redis", "airflow": "Airflow", "spark": "Spark"
    }
    
    found_skills = []
    for keyword, canonical in SKILL_MAP.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            if canonical not in found_skills:
                found_skills.append(canonical)
                
    # 2. Remote / On-site / WFH
    remote_only = None
    if re.search(r"\b(remote|wfh|work from home|online)\b", text):
        remote_only = True
    elif re.search(r"\b(on[- ]?site|in[- ]?office|offline)\b", text):
        remote_only = False
        
    # 3. Location extraction (Any Indian tech hub or global)
    location = None
    cities = {
        "bengaluru": "Bengaluru", "bangalore": "Bengaluru",
        "gurugram": "Gurugram", "gurgaon": "Gurugram", "delhi": "Delhi", "ncr": "Gurugram",
        "mumbai": "Mumbai", "pune": "Pune", "hyderabad": "Hyderabad",
        "chennai": "Chennai", "noida": "Noida", "kolkata": "Kolkata"
    }
    for alias, formal_name in cities.items():
        if re.search(rf"\b{re.escape(alias)}\b", text):
            location = formal_name
            break
            
    # 4. Stipend detection (handles "50k", "50000", "paying 30k+", "above 40,000", "min 20k")
    min_stipend = None
    match_k = re.search(r"(\d{1,3})\s*(k|thousand)", text)
    if match_k:
        min_stipend = int(match_k.group(1)) * 1000
    else:
        match_num = re.search(r"(?:stipend|paying|above|min|salary|₹|rs\.?)\s*(\d{4,6})", text)
        if match_num:
            min_stipend = int(match_num.group(1))
            
    # 5. Role & Domain detection
    role = None
    if re.search(r"\b(backend|server|api|database)\b", text):
        role = "Backend"
    elif re.search(r"\b(ai|llm|ml|machine learning|nlp|data science)\b", text):
        role = "AI"
    elif re.search(r"\b(full[- ]?stack|fullstack)\b", text):
        role = "Full Stack"
    elif re.search(r"\b(frontend|ui|ux|web)\b", text):
        role = "Frontend"
    elif re.search(r"\b(devops|sre|cloud|infrastructure)\b", text):
        role = "DevOps"
    elif re.search(r"\b(data|etl|analytics)\b", text):
        role = "Data"
        
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
    
    # 1. Store chat history
    cursor.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (user_id, message))
    
    # 2. Dynamically parse intent
    filters = parse_user_intent_dynamic(message)
    tools_called = []
    
    # 3. Update memory whenever user mentions new skills, target location, or stipend
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    current_skills = json.loads(user["skills"]) if user and user["skills"] else []
    
    if filters.skills or filters.min_stipend or filters.location:
        updated_skills = list(set(current_skills + filters.skills))
        cursor.execute("""
        UPDATE users 
        SET skills = ?, 
            preferred_locations = CASE WHEN ? IS NOT NULL THEN json_array(?) ELSE preferred_locations END,
            min_stipend = COALESCE(?, min_stipend),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (json.dumps(updated_skills), filters.location, filters.location, filters.min_stipend, user_id))
        tools_called.append("update_user_preferences")
        
    # 4. Search and rank internships
    tools_called.append("search_jobs")
    matched_jobs = search_and_rank_jobs(
        user_id=user_id,
        target_role=filters.role,
        location=filters.location,
        remote_only=filters.remote_only,
        min_stipend=filters.min_stipend,
        limit=5
    )
    
    # 5. Formulate human-like conversational response for ANY comment
    text_lower = message.lower().strip()
    greetings = ["hi", "hello", "hey", "sup", "greetings", "good morning", "good evening"]
    
    if any(text_lower == g or text_lower.startswith(g + " ") for g in greetings):
        reply = (
            f"👋 Hello! Great to meet you! I've loaded your profile context with skills like "
            f"{', '.join(current_skills[:3]) if current_skills else 'Python & Engineering'}.\n\n"
            f"Here are {len(matched_jobs)} top opportunities currently open for you. "
            f"You can tell me anything like: *'I want remote roles only'*, *'filter above ₹50k'*, "
            f"or *'I also know React and Docker'* to instantly re-rank them!"
        )
    elif "who are you" in text_lower or "what can you do" in text_lower or "help" in text_lower:
        reply = (
            f"🤖 I am **RoleRadar**, your conversational AI Career Agent.\n"
            f"• I remember your skills, target locations, and preferences across conversations.\n"
            f"• I use hybrid SQL + semantic search to match and rank real internships based on your profile.\n"
            f"• You can give me any preference (e.g. *'Show me AI startups in Gurugram'* or *'Roles paying >60k'*) and I'll find them!"
        )
    elif matched_jobs:
        top = matched_jobs[0]
        skill_str = ", ".join(top['skills_required'][:4])
        reply = (
            f"🎯 Found **{len(matched_jobs)} matching internships** for your request:\n\n"
            f"⭐ **Top Match: {top['title']} at {top['company']}**\n"
            f"📍 {top['location']} {'(Remote Available 🌐)' if top['is_remote'] else ''}\n"
            f"💰 ₹{top['stipend']:,}/month  |  📊 **{top['match_pct']}% Profile Match**\n"
            f"🛠️ Tech: {skill_str}\n\n"
            f"Check the ranked cards on the right. Would you like to refine by tech stack, stipend, or location?"
        )
    else:
        # Graceful fallback: If hard filters yielded 0, fall back to top overall internships
        cursor.execute("SELECT * FROM jobs WHERE is_active = 1 LIMIT 4")
        fallback_rows = cursor.fetchall()
        matched_jobs = [
            {
                "id": r["id"],
                "title": r["title"],
                "company": r["company"],
                "location": r["location"],
                "is_remote": bool(r["is_remote"]),
                "stipend": r["stipend"],
                "skills_required": json.loads(r["skills_required"]) if r["skills_required"] else [],
                "requirements_text": r["requirements_text"],
                "score": 0.75,
                "match_pct": 75
            }
            for r in fallback_rows
        ]
        reply = (
            f"I didn't find exact listings with those strict constraints, but here are the "
            f"top featured engineering internships currently hiring! You can adjust your location, "
            f"role, or stipend preferences anytime."
        )
        
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

