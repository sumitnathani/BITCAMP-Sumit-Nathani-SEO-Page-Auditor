import json
import sys
import traceback
import requests
from bs4 import BeautifulSoup
from tinyfish import TinyFish

def run_seo_audit(url, target_query=None):
    client = TinyFish()
    report = {"url": url, "status": "running"}
    
    # 1. Raw HTML & Visible Text Analysis
    try:
        raw_resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=15)
        soup = BeautifulSoup(raw_resp.text, "html.parser")
        
        page_title = soup.title.string.strip() if soup.title else "No Title Found"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"] if meta_desc_tag and "content" in meta_desc_tag.attrs else "No Meta Description"
        
        json_ld_blocks = soup.find_all("script", type="application/ld+json")
        has_json_ld = len(json_ld_blocks) > 0
        
        headings = {"h1": len(soup.find_all("h1")), "h2": len(soup.find_all("h2"))}

        for tag in soup(["script", "style"]):
            tag.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)
        visible_len = len(visible_text)
    except Exception as e:
        return {"url": url, "status": "error", "step": "raw_html", "message": str(e)}

    # 2. TinyFish Fetch Coverage
    fetched_text = ""
    try:
        fetch_result = client.fetch.get_contents(urls=[url])
        if hasattr(fetch_result, 'errors') and fetch_result.errors:
            fetch_status = f"fetch_errors: {fetch_result.errors}"
        else:
            if fetch_result.results and len(fetch_result.results) > 0:
                fetched_text = fetch_result.results[0].text
    except Exception as e:
        pass # Fallback to empty fetched text if fetch fails

    fetched_len = len(fetched_text)
    coverage_ratio = round(fetched_len / visible_len, 3) if visible_len > 0 else 0

    # 3. TinyFish Search Visibility Check
    query_to_use = target_query or page_title
    search_ranked = False
    search_position = None
    search_snippet = None
    
    try:
        search_result = client.search.query(
            query=query_to_use,
            location="IN",
            language="en"
        )
        if search_result and hasattr(search_result, 'results'):
            for idx, item in enumerate(search_result.results, start=1):
                if url.lower() in item.url.lower():
                    search_ranked = True
                    search_position = idx
                    search_snippet = item.snippet
                    break
    except Exception as e:
        pass # Fallback if search fails

    # 4. Synthesize Issues & Verdicts
    issues = []
    if coverage_ratio < 0.4:
        issues.append({
            "type": "js_rendered_content",
            "severity": "high",
            "detail": f"AI tools see only {int(coverage_ratio * 100)}% of your visible page content ({fetched_len} vs {visible_len} chars).",
            "fix": "Implement Server-Side Rendering (SSR) or pre-rendering so crawlers and AI bots can read the text immediately."
        })
    
    if not has_json_ld:
        issues.append({
            "type": "missing_structured_data",
            "severity": "medium",
            "detail": "No JSON-LD schema.org blocks found on the page.",
            "fix": "Add relevant schema markup (Article, Product, Organization) to help AI search engines understand your entities."
        })
        
    if headings["h1"] == 0:
        issues.append({
            "type": "missing_h1",
            "severity": "medium",
            "detail": "No H1 heading tag found in raw markup.",
            "fix": "Ensure every page has a single clear H1 tag summarizing the core topic."
        })
        
    if not search_ranked:
        issues.append({
            "type": "visibility_gap",
            "severity": "high",
            "detail": f"Page is not currently ranking in top search results for query: '{query_to_use}'.",
            "fix": "Address the rendering and structural gaps above to ensure search engines can successfully index and cite your content."
        })

    report = {
        "url": url,
        "status": "success",
        "page_title": page_title,
        "meta_description": meta_desc,
        "metrics": {
            "visible_text_length": visible_len,
            "fetched_text_length": fetched_len,
            "coverage_ratio": coverage_ratio,
            "has_json_ld": has_json_ld,
            "headings": headings
        },
        "search_visibility": {
            "query_used": query_to_use,
            "ranked": search_ranked,
            "position": search_position,
            "snippet": search_snippet
        },
        "issues_detected": issues
    }

    return report

if __name__ == "__main__":
    try:
        audit = run_seo_audit("https://www.notion.so", target_query="Notion AI workspace")
        print(json.dumps(audit, indent=2))
    except Exception as e:
        error_output = {"status": "fatal_error", "message": str(e), "traceback": traceback.format_exc()}
        print(json.dumps(error_output, indent=2))