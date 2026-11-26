import json
import sqlite3
import random
from database import get_db_connection, init_db

# Curated, realistic Software & AI Internships across India with detailed company info & remote options
INTERNSHIPS = [
    # --- KOLKATA & EASTERN REGION ---
    {
        "title": "Cybersecurity & Network Systems Intern",
        "company": "Vehere",
        "location": "Kolkata (Salt Lake Sector V) / Remote",
        "is_remote": 1,
        "stipend": 55000,
        "skills_required": ["Python", "C++", "Linux", "Networking", "Docker"],
        "requirements_text": "Develop packet inspection modules, network telemetry pipelines, and threat-hunting microservices for enterprise NDR platforms.",
        "about_company": "Vehere is a premier cybersecurity pioneer headquartered in Kolkata (Salt Lake Sector V). It specializes in AI-powered Network Detection & Response (NDR), Cyber Situational Awareness, and enterprise packet intelligence for national security agencies and Fortune 500 enterprises."
    },
    {
        "title": "AI & Decision Analytics Intern",
        "company": "Tredence Analytics",
        "location": "Kolkata (Sector V) / Remote",
        "is_remote": 1,
        "stipend": 50000,
        "skills_required": ["Python", "SQL", "PyTorch", "Pandas", "Scikit-Learn"],
        "requirements_text": "Build predictive machine learning models, supply chain demand forecasting algorithms, and customer analytics pipelines.",
        "about_company": "Tredence Analytics is a global data science solutions unicorn operating major delivery labs in Kolkata (Victoria Park, Salt Lake Sector V) and Bengaluru. It bridges the gap between deep analytics and real-world business execution for global retail, CPG, and healthcare giants."
    },
    {
        "title": "Full Stack Cloud Intern",
        "company": "Indus Net Technologies (INT)",
        "location": "Kolkata (New Town / Ecospace) / Hybrid",
        "is_remote": 1,
        "stipend": 38000,
        "skills_required": ["React", "Node.js", "TypeScript", "PostgreSQL", "AWS"],
        "requirements_text": "Design scalable enterprise SaaS interfaces, microservices, and secure digital banking portals using modern cloud-native architectures.",
        "about_company": "Indus Net Technologies (INT) is an award-winning digital transformation and product innovation powerhouse operating from Ecospace Business Park, New Town, Kolkata. INT designs high-throughput digital banking, fintech, and enterprise enterprise cloud systems across 20+ countries."
    },
    {
        "title": "Fintech Backend Engineer Intern",
        "company": "Senrysa Technologies",
        "location": "Kolkata (Salt Lake) / Remote",
        "is_remote": 1,
        "stipend": 42000,
        "skills_required": ["Java", "Spring Boot", "SQL", "Microservices", "REST APIs"],
        "requirements_text": "Build resilient high-availability financial inclusion payment switches, biometric auth APIs, and core transactional databases.",
        "about_company": "Senrysa Technologies is an eastern India fintech software leader based in Kolkata. It powers rural banking, Aadhaar-enabled payment systems (AePS), and smart-card transactional architectures impacting over 50 million citizens."
    },

    # --- HYDERABAD ---
    {
        "title": "AI & Autonomous Finance Intern",
        "company": "HighRadius",
        "location": "Hyderabad (HITEC City / Madhapur)",
        "is_remote": 1,
        "stipend": 65000,
        "skills_required": ["Python", "FastAPI", "SQL", "Machine Learning", "Docker"],
        "requirements_text": "Develop autonomous accounting agents, cash flow prediction models, and real-time ledger data synchronization services.",
        "about_company": "HighRadius is a global SaaS unicorn headquartered in Hyderabad (HITEC City). Powered by its proprietary 'Rivana AI' engine, HighRadius automates order-to-cash, treasury, and autonomous financial reconciliation for multinational corporations."
    },
    {
        "title": "SaaS Platform Engineering Intern",
        "company": "Darwinbox",
        "location": "Hyderabad (Madhapur) / Remote",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["Python", "Go", "PostgreSQL", "Kafka", "Redis"],
        "requirements_text": "Build distributed HR-tech enterprise services, event-driven notification systems, and high-load database indexing layers.",
        "about_company": "Darwinbox is an enterprise HR-tech unicorn backed by Salesforce Ventures, headquartered in Hyderabad. It delivers mobile-first, AI-driven human capital management to over 850 global enterprises and 2.5 million employees worldwide."
    },
    {
        "title": "Aerospace Flight Software Intern",
        "company": "Skyroot Aerospace",
        "location": "Hyderabad (Gachibowli / T-Hub)",
        "is_remote": 0,
        "stipend": 50000,
        "skills_required": ["C++", "Python", "Linux", "Embedded Systems", "Algorithms"],
        "requirements_text": "Develop telemetry data ingestion daemons, hardware-in-the-loop simulation software, and rocket flight computer control logic.",
        "about_company": "Skyroot Aerospace is India's pioneer private space-tech unicorn headquartered in Hyderabad. It made history launching India's first privately developed rocket (Vikram-S) and builds flexible, on-demand satellite orbital launch vehicles."
    },
    {
        "title": "Cloud Platform Architect Intern",
        "company": "Zenoti",
        "location": "Hyderabad / Remote",
        "is_remote": 1,
        "stipend": 58000,
        "skills_required": ["React", "C#", ".NET", "Azure", "SQL"],
        "requirements_text": "Design multi-tenant enterprise booking microservices, real-time calendar syncing, and POS cloud payment integrations.",
        "about_company": "Zenoti is an enterprise cloud SaaS unicorn founded in Hyderabad. It provides an all-in-one management, booking, and POS software platform powering thousands of luxury spas, salons, and wellness centers worldwide."
    },

    # --- PUNE & WESTERN INDIA ---
    {
        "title": "Cloud Data Resilience Intern",
        "company": "Druva",
        "location": "Pune (Baner) / Remote",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["Python", "AWS", "Docker", "Linux", "Distributed Systems"],
        "requirements_text": "Implement cloud backup replication microservices, snapshot deduplication algorithms, and ransomware threat telemetry.",
        "about_company": "Druva is a 100% SaaS-based cloud data protection and cyber-resilience unicorn with primary Indian engineering headquarters in Pune. It protects mission-critical enterprise workloads across AWS, Microsoft 365, and multi-cloud environments."
    },
    {
        "title": "Enterprise AI & Contract Intelligence Intern",
        "company": "Icertis",
        "location": "Pune / Remote",
        "is_remote": 1,
        "stipend": 62000,
        "skills_required": ["Python", "FastAPI", "NLP", "Azure", "PostgreSQL"],
        "requirements_text": "Build semantic contract parsing pipelines, clause extraction with generative AI, and compliance evaluation engines.",
        "about_company": "Icertis is the global leader in AI-powered Contract Lifecycle Management (CLM) headquartered between Pune and Bellevue, WA. It transforms enterprise contracts into structured, actionable business intelligence for Fortune 100 enterprises."
    },
    {
        "title": "Cybersecurity & Endpoint Protection Intern",
        "company": "Quick Heal Technologies",
        "location": "Pune (Shivaji Nagar) / Hybrid",
        "is_remote": 0,
        "stipend": 45000,
        "skills_required": ["C++", "Python", "Windows Internals", "Linux", "Reverse Engineering"],
        "requirements_text": "Develop heuristic malware detection engines, kernel-level behavioral monitors, and automated threat intelligence feeds.",
        "about_company": "Quick Heal Technologies is India's premier homegrown cybersecurity software manufacturer, based in Pune. It builds antivirus, endpoint security, and enterprise data encryption products protecting millions of users globally."
    },

    # --- BENGALURU & SOUTHERN TECH HUBS ---
    {
        "title": "Software Engineering Intern",
        "company": "BrowserStack",
        "location": "Bengaluru / Mumbai / Remote",
        "is_remote": 1,
        "stipend": 65000,
        "skills_required": ["Python", "FastAPI", "SQL", "Docker", "Linux"],
        "requirements_text": "Build scalable cloud infrastructure test runners and developer telemetry pipelines. Design modular backend APIs.",
        "about_company": "BrowserStack is the world's leading cloud web & mobile testing platform, supporting over 2 million tests daily. It gives developers instant access to thousands of real devices and browsers directly in the cloud."
    },
    {
        "title": "AI & Multilingual LLM Intern",
        "company": "Sarvam AI",
        "location": "Bengaluru / Hybrid",
        "is_remote": 1,
        "stipend": 70000,
        "skills_required": ["Python", "PyTorch", "NLP", "LLMs", "Vector DB"],
        "requirements_text": "Fine-tune open-source models, curate multilingual speech and Indian language datasets, and build evaluation pipelines.",
        "about_company": "Sarvam AI is India's sovereign AI research organization building full-stack foundational generative models and speech-to-text systems tailored specifically for Indian languages and enterprise use cases."
    },
    {
        "title": "Backend Engineering Intern",
        "company": "Razorpay",
        "location": "Bengaluru / Remote",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["Go", "Python", "PostgreSQL", "Kafka", "Docker"],
        "requirements_text": "Design scalable RESTful APIs, optimize high-throughput database queries, and manage microservices.",
        "about_company": "Razorpay is India's premier fintech payments unicorn based in Bengaluru. It powers online payment gateways, automated settlements, banking, and payroll infrastructure for millions of businesses across India."
    },
    {
        "title": "Developer Tooling & API Intern",
        "company": "Postman",
        "location": "Bengaluru / Remote",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["React", "TypeScript", "Node.js", "Electron", "PostgreSQL"],
        "requirements_text": "Develop intuitive collaborative developer workspaces, WebSocket syncing, and performant UI components.",
        "about_company": "Postman is the globally dominant API collaboration and development platform used by over 30 million software engineers. It streamlines API lifecycle design, mocking, testing, and continuous monitoring."
    },
    {
        "title": "Data Engineering & Pipeline Intern",
        "company": "Zepto",
        "location": "Bengaluru / Mumbai",
        "is_remote": 0,
        "stipend": 55000,
        "skills_required": ["Python", "SQL", "Snowflake", "Airflow", "Spark"],
        "requirements_text": "Build real-time ETL data pipelines, monitor warehouse performance, and write complex analytics queries.",
        "about_company": "Zepto is India's hyper-growth 10-minute quick commerce unicorn, operating dark stores and AI-driven inventory prediction networks across all major Indian metropolitan areas."
    },
    {
        "title": "Healthcare Cloud SaaS Intern",
        "company": "CareStack",
        "location": "Kochi (Infopark) / Remote",
        "is_remote": 1,
        "stipend": 45000,
        "skills_required": ["C#", ".NET", "React", "SQL Server", "Azure"],
        "requirements_text": "Engineer clinical workflow management systems, patient scheduling engines, and automated insurance claims processing.",
        "about_company": "CareStack is a flagship health-tech SaaS company originating from Infopark Kochi. It delivers a modern, cloud-based practice management platform for dental healthcare practices throughout North America."
    },

    # --- DELHI NCR & GURUGRAM ---
    {
        "title": "Generative Video AI Intern",
        "company": "InVideo",
        "location": "Mumbai / Delhi NCR / Remote",
        "is_remote": 1,
        "stipend": 60000,
        "skills_required": ["Python", "FastAPI", "OpenAI", "Prompt Engineering", "SQL"],
        "requirements_text": "Build agentic video scripting workflows, parse structured output schemas, and evaluate prompt variations.",
        "about_company": "InVideo is an intuitive generative AI video creation platform serving millions of content creators worldwide. It turns plain text prompts into full-production video assets with synchronized voiceovers and scenes."
    },
    {
        "title": "Full Stack Platform Intern",
        "company": "Urban Company",
        "location": "Gurugram / Remote",
        "is_remote": 1,
        "stipend": 50000,
        "skills_required": ["Python", "Django", "React", "Redis", "PostgreSQL"],
        "requirements_text": "Develop partner dispatch algorithms and implement Redis caching for high availability.",
        "about_company": "Urban Company is Asia's largest home services marketplace unicorn based in Gurugram, connecting millions of verified service professionals with urban households using precision matchmaking algorithms."
    },

    # --- EMERGING TECH HUBS & TIER-2 CITIES ---
    {
        "title": "Automotive AI & Marketplace Intern",
        "company": "CarDekho",
        "location": "Jaipur / Gurugram / Remote",
        "is_remote": 1,
        "stipend": 48000,
        "skills_required": ["Python", "Django", "React", "SQL", "AWS"],
        "requirements_text": "Develop auto-valuation pricing ML models, customer recommendation engines, and inventory management APIs.",
        "about_company": "CarDekho (GirnarSoft) is North India's premier automotive tech unicorn headquartered in Jaipur. It operates CarDekho, ZigWheels, and insurtech platforms driving automotive discovery and commerce across India and Southeast Asia."
    },
    {
        "title": "Civic-Tech & Enterprise Platform Intern",
        "company": "CSM Technologies",
        "location": "Bhubaneswar (InfoCity) / Hybrid",
        "is_remote": 1,
        "stipend": 40000,
        "skills_required": ["Java", "Spring Boot", "Angular", "PostgreSQL", "Docker"],
        "requirements_text": "Design digital public infrastructure, mining governance systems, and large-scale government enterprise web portals.",
        "about_company": "CSM Technologies is a digital transformation pioneer headquartered in Bhubaneswar (InfoCity). It crafts mission-critical civic-tech, e-governance platforms, and logistics tracking for governments across India and Africa."
    },
    {
        "title": "HealthTech & Preventive AI Intern",
        "company": "Fitelo",
        "location": "Chandigarh / Remote",
        "is_remote": 1,
        "stipend": 42000,
        "skills_required": ["React Native", "Node.js", "Python", "MongoDB", "Firebase"],
        "requirements_text": "Develop conversational nutrition habit tracking features, automated diet plan recommenders, and seamless user health logging.",
        "about_company": "Fitelo is a fast-growing digital health and nutrition wellness startup headquartered in Chandigarh. It provides AI-assisted, personalized diet and lifestyle management apps to hundreds of thousands of users globally."
    }
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if about_company column exists in jobs, if not alter table safely
    try:
        cursor.execute("SELECT about_company FROM jobs LIMIT 1")
    except Exception:
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN about_company TEXT")
            conn.commit()
        except Exception:
            pass

    # Clear and re-populate with rich dataset
    try:
        cursor.execute("DELETE FROM jobs")
        conn.commit()
    except Exception:
        pass
        
    random.seed(42)
    # Generate mock 768-dim normalized embedding vectors for deterministic testing
    for item in INTERNSHIPS:
        vec = [random.gauss(0, 1) for _ in range(768)]
        norm = sum(x**2 for x in vec) ** 0.5
        norm_vec = [round(x / norm, 5) for x in vec]
        
        cursor.execute("""
        INSERT INTO jobs (title, company, location, is_remote, stipend, skills_required, requirements_text, about_company, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["title"],
            item["company"],
            item["location"],
            item["is_remote"],
            item["stipend"],
            json.dumps(item["skills_required"]),
            item["requirements_text"],
            item.get("about_company", ""),
            json.dumps(norm_vec)
        ))
        
    # Seed default user with expanded locations
    cursor.execute("""
    INSERT OR REPLACE INTO users (id, name, skills, preferred_locations, target_roles, min_stipend)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "student_user_1",
        "Sougata Mandal",
        json.dumps(["Python", "SQL", "FastAPI", "React"]),
        json.dumps(["Kolkata", "Hyderabad", "Bengaluru", "Pune", "Remote"]),
        json.dumps(["Software Engineering Intern", "AI Intern", "Backend Intern"]),
        35000
    ))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully with expanded company & Indian city data!")
