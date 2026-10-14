import json
from dtu_seo_auditor import run_seo_audit

# Test URLs with their respective target search queries
TARGETS = [
    {"url": "https://www.notion.so", "query": "Notion AI workspace"},
    {"url": "https://en.wikipedia.org/wiki/Artificial_intelligence", "query": "Artificial intelligence overview"}
]

if __name__ == "__main__":
    batch_results = []
    for target in TARGETS:
        report = run_seo_audit(target["url"], target_query=target["query"])
        batch_results.append(report)
    
    print("\n========== BATCH AUDIT SUMMARY ==========")
    print(json.dumps(batch_results, indent=2))