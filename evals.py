import time
from agent import parse_user_intent_dynamic
from search import search_and_rank_jobs
from database import init_db
from seed_data import seed_database

EVAL_BENCHMARK = [
    {
        "query": "Remote Python internships paying above 50k",
        "expected_skills": ["Python"],
        "expected_remote": True,
        "expected_min_stipend": 50000,
        "relevant_company": "Elip"
    },
    {
        "query": "Backend roles in Bengaluru with SQL and Docker",
        "expected_skills": ["SQL", "Docker"],
        "expected_remote": None,
        "expected_min_stipend": None,
        "relevant_company": "Swiggy"
    },
    {
        "query": "AI research internship in Bengaluru paying at least 60k",
        "expected_skills": [],
        "expected_remote": None,
        "expected_min_stipend": 60000,
        "relevant_company": "Sarvam AI"
    },
    {
        "query": "React and Node.js full stack internship",
        "expected_skills": ["React", "Node.js"],
        "expected_remote": None,
        "expected_min_stipend": None,
        "relevant_company": "Razorpay"
    },
    {
        "query": "Looking for DevOps or Cloud roles with AWS and Docker",
        "expected_skills": ["Docker", "AWS"],
        "expected_remote": None,
        "expected_min_stipend": None,
        "relevant_company": "BrowserStack"
    }
]

def run_evaluations():
    init_db()
    seed_database()
    
    print("\n==========================================")
    print("   RoleRadar Automated Evaluation Suite   ")
    print("==========================================")
    
    total = len(EVAL_BENCHMARK)
    schema_correct = 0
    recall_at_5_hits = 0
    latencies = []
    
    for idx, test_case in enumerate(EVAL_BENCHMARK, 1):
        start = time.time()
        
        # 1. Evaluate intent filter extraction accuracy
        extracted = parse_user_intent_dynamic(test_case["query"])
        
        # Check correctness
        skills_match = all(s in extracted.skills for s in test_case["expected_skills"])
        remote_match = (extracted.remote_only == test_case["expected_remote"])
        stipend_match = (extracted.min_stipend == test_case["expected_min_stipend"])
        
        if skills_match and remote_match and stipend_match:
            schema_correct += 1
            
        # 2. Evaluate Retrieval Recall@5
        results = search_and_rank_jobs(
            user_id="student_user_1",
            target_role=extracted.role,
            location=extracted.location,
            remote_only=extracted.remote_only,
            min_stipend=extracted.min_stipend,
            limit=5
        )
        
        companies_returned = [r["company"] for r in results]
        hit = any(test_case["relevant_company"].lower() in c.lower() for c in companies_returned)
        if hit:
            recall_at_5_hits += 1
            
        elapsed = (time.time() - start) * 1000
        latencies.append(elapsed)
        
        status = "PASSED" if hit else "MISSED"
        print(f"[{idx}/{total}] \"{test_case['query'][:35]}...\" -> {status} ({elapsed:.1f}ms)")
        
    avg_latency = sum(latencies) / len(latencies)
    schema_acc = (schema_correct / total) * 100
    recall_5 = (recall_at_5_hits / total) * 100
    
    print("\n================ EVAL SUMMARY ================")
    print(f"• Tool & Structured Output Accuracy : {schema_acc:.1f}%")
    print(f"• Retrieval Recall@5                : {recall_5:.1f}%")
    print(f"• Mean Query Latency                : {avg_latency:.2f} ms")
    print("==============================================\n")

if __name__ == "__main__":
    run_evaluations()

