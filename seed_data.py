import json
import sqlite3
import random
from database import get_db_connection, init_db

# 25 Diverse, Realistic Software/AI Internships in India
INTERNSHIPS = [
    {
        "title": "Software Engineering Intern",
        "company": "Elip (YC W25)",
        "location": "Gurugram / Bengaluru",
        "is_remote": 1,
        "stipend": 75000,
        "skills_required": ["Python", "FastAPI", "SQL", "LLMs", "Docker"],
        "requirements_text": "Build LLM-powered conversational agents that use tools and remember context. Hybrid retrieval and semantic search over changing indices. Evaluate LLM outputs."
    },
    {
        "title": "Backend Engineering Intern",
        "company": "Swiggy",
        "location": "Bengaluru",
        "is_remote": 0,
        "stipend": 60000,
        "skills_required": ["Go", "Python", "PostgreSQL", "Kafka", "Docker"],
        "requirements_text": "Design scalable RESTful APIs, optimize high-throughput database queries, and manage microservices."
    },
    {
        "title": "AI/ML Intern",
        "company": "Sarvam AI",
        "location": "Bengaluru",
        "is_remote": 0,
        "stipend": 70000,
        "skills_required": ["Python", "PyTorch", "NLP", "LLMs", "Vector DB"],
        "requirements_text": "Fine-tune open-source models, curate multilingual speech and text datasets, and build evaluation pipelines."
    },
    {
        "title": "Full Stack Developer Intern",
        "company": "Razorpay",
        "location": "Bengaluru",
        "is_remote": 1,
        "stipend": 50000,
        "skills_required": ["React", "Node.js", "TypeScript", "PostgreSQL"],
        "requirements_text": "Develop intuitive checkout UI components and robust backend payment webhook handlers."
    },
    {
        "title": "Data Engineering Intern",
        "company": "Zepto",
        "location": "Mumbai",
        "is_remote": 0,
        "stipend": 55000,
        "skills_required": ["Python", "SQL", "Snowflake", "Airflow", "Spark"],
        "requirements_text": "Build real-time ETL data pipelines, monitor warehouse performance, and write complex analytics queries."
    },
    {
        "title": "Generative AI Research Intern",
        "company": "Krutrim",
        "location": "Bengaluru",
        "is_remote": 1,
        "stipend": 65000,
        "skills_required": ["Python", "Transformers", "RAG", "Embeddings", "FastAPI"],
        "requirements_text": "Implement state-of-the-art retrieval-augmented generation (RAG) agents with dynamic context filtering."
    },
    {
        "title": "Frontend Engineer Intern",
        "company": "Postman",
        "location": "Bengaluru",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["React", "TypeScript", "Electron", "CSS", "Jest"],
        "requirements_text": "Craft modular API testing interfaces, optimize client-side rendering speed, and ensure high test coverage."
    },
    {
        "title": "DevOps & Cloud Intern",
        "company": "BrowserStack",
        "location": "Mumbai",
        "is_remote": 1,
        "stipend": 50000,
        "skills_required": ["Docker", "Kubernetes", "AWS", "Linux", "Terraform"],
        "requirements_text": "Automate CI/CD pipelines, monitor cloud cluster health, and optimize container build caches."
    },
    {
        "title": "Python Backend Intern",
        "company": "Urban Company",
        "location": "Gurugram",
        "is_remote": 0,
        "stipend": 45000,
        "skills_required": ["Python", "Django", "Redis", "PostgreSQL"],
        "requirements_text": "Develop partner dispatch algorithms and implement Redis caching for high availability."
    },
    {
        "title": "Applied AI Intern",
        "company": "InVideo",
        "location": "Mumbai",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["Python", "FastAPI", "OpenAI", "Prompt Engineering", "SQL"],
        "requirements_text": "Build agentic video scripting workflows, parse structured output schemas, and evaluate prompt variations."
    }
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    try:
        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        row = cursor.fetchone()
        if row and row["count"] > 0:
            conn.close()
            return
    except Exception:
        pass
        
    random.seed(42)
    # Generate mock 768-dim normalized embedding vectors for deterministic testing
    for item in INTERNSHIPS:
        # Pseudo vector seeded by title hash
        vec = [random.gauss(0, 1) for _ in range(768)]
        norm = sum(x**2 for x in vec) ** 0.5
        norm_vec = [round(x / norm, 5) for x in vec]
        
        cursor.execute("""
        INSERT INTO jobs (title, company, location, is_remote, stipend, skills_required, requirements_text, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["title"],
            item["company"],
            item["location"],
            item["is_remote"],
            item["stipend"],
            json.dumps(item["skills_required"]),
            item["requirements_text"],
            json.dumps(norm_vec)
        ))
        
    # Seed default user
    cursor.execute("""
    INSERT OR REPLACE INTO users (id, name, skills, preferred_locations, target_roles, min_stipend)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "student_user_1",
        "Sougata Mandal",
        json.dumps(["Python", "SQL", "FastAPI"]),
        json.dumps(["Gurugram", "Bengaluru", "Remote"]),
        json.dumps(["Software Engineering Intern", "Backend Intern"]),
        30000
    ))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded with realistic internships and demo student profile.")
