import streamlit as st
import requests
from bs4 import BeautifulSoup
from tinyfish import TinyFish

# Page Configuration
st.set_page_config(
    page_title="DTU: SEO Page Auditor",
    page_icon="🤖",
    layout="wide"
)

# Initialize TinyFish Client
@st.cache_resource
def get_tinyfish_client():
    return TinyFish()

client = get_tinyfish_client()

# Core Audit Function
def run_seo_audit(url, target_query=None):
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
        return {"error": f"Failed to parse raw HTML: {str(e)}"}

    # 2. TinyFish Fetch Coverage
    fetched_text = ""
    try:
        fetch_result = client.fetch.get_contents(urls=[url])
        if hasattr(fetch_result, 'errors') and fetch_result.errors:
            pass
        else:
            if fetch_result.results and len(fetch_result.results) > 0:
                fetched_text = fetch_result.results[0].text
    except Exception as e:
        pass

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
        pass

    # 4. Synthesize Issues
    issues = []
    if coverage_ratio < 0.4:
        issues.append({
            "type": "js_rendered_content",
            "severity": "High",
            "detail": f"AI tools see only {int(coverage_ratio * 100)}% of your visible page content ({fetched_len} vs {visible_len} chars).",
            "fix": "Implement Server-Side Rendering (SSR) or pre-rendering so AI crawlers can read the text immediately."
        })
    
    if not has_json_ld:
        issues.append({
            "type": "missing_structured_data",
            "severity": "Medium",
            "detail": "No JSON-LD schema.org blocks found on the page.",
            "fix": "Add schema markup (Article, Product, Organization) to help AI engines understand entities."
        })
        
    if headings["h1"] == 0:
        issues.append({
            "type": "missing_h1",
            "severity": "Medium",
            "detail": "No H1 heading tag found in raw markup.",
            "fix": "Ensure every page has a single clear H1 tag summarizing the core topic."
        })
        
    if not search_ranked:
        issues.append({
            "type": "visibility_gap",
            "severity": "High",
            "detail": f"Page is not currently ranking in top search results for query: '{query_to_use}'.",
            "fix": "Address the rendering and structural gaps above to ensure search engines index and cite your content."
        })

    return {
        "url": url,
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

# --- UI Layout ---
st.title("🤖 DTU: AI SEO Page Auditor")
st.markdown("From the TinyFish × DTU workshop. Audit whether AI search and fetch tools can actually read, understand, and rank your web pages.")

# Sidebar Controls
st.sidebar.header("Audit Controls")
target_url = st.sidebar.text_input("Target URL", value="https://www.notion.so")
target_query = st.sidebar.text_input("Target Search Query (Optional)", value="Notion AI workspace")

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Quick Demo Presets")
col_p1, col_p2 = st.sidebar.columns(2)
if col_p1.button("Test Notion (SPA)"):
    target_url = "https://www.notion.so"
    target_query = "Notion AI workspace"
if col_p2.button("Test Wikipedia"):
    target_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    target_query = "Artificial intelligence overview"

run_btn = st.sidebar.button("Run AI SEO Audit", type="primary", use_container_width=True)

# Main Execution
if run_btn:
    with st.spinner(f"Analyzing live page and querying TinyFish APIs for {target_url}..."):
        report = run_seo_audit(target_url, target_query)
        
    if "error" in report:
        st.error(report["error"])
    else:
        st.success(f"Audit completed successfully for: {report['page_title']}")
        
        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        cov_pct = int(report['metrics']['coverage_ratio'] * 100)
        col1.metric("AI Readability Coverage", f"{cov_pct}%", delta="Target: >80%", delta_color="normal" if cov_pct > 40 else "inverse")
        col2.metric("Visible Text (Raw HTML)", f"{report['metrics']['visible_text_length']:,} chars")
        col3.metric("AI Extracted (Fetch)", f"{report['metrics']['fetched_text_length']:,} chars")
        
        search_status = f"Ranked #{report['search_visibility']['position']}" if report['search_visibility']['ranked'] else "Not Ranking"
        col4.metric("Search Visibility", search_status)
        
        # Tabs for detailed breakdown
        tab1, tab2, tab3, tab4 = st.tabs(["🚨 Issues & Fixes", "📊 Metrics Breakdown", "🔍 Search Snippet Preview", "ℹ️ How TinyFish is Used"])
        
        with tab1:
            st.subheader("Actionable AI-SEO Fixes")
            if not report["issues_detected"]:
                st.success("No critical AI-readability or visibility issues detected! Page is fully optimized.")
            else:
                for issue in report["issues_detected"]:
                    severity_color = "red" if issue["severity"] == "High" else "orange"
                    st.markdown(f"### :{severity_color}[{issue['severity']} Severity] — {issue['type'].replace('_', ' ').title()}")
                    st.markdown(f"**Finding:** {issue['detail']}")
                    st.info(f"💡 **Recommended Fix:** {issue['fix']}")
                    st.markdown("---")
                    
        with tab2:
            st.subheader("Page Metadata & Structure")
            st.write(f"**Page Title:** {report['page_title']}")
            st.write(f"**Meta Description:** {report['meta_description']}")
            st.write(f"**JSON-LD Structured Data:** {'✅ Found' if report['metrics']['has_json_ld'] else '❌ Missing'}")
            st.write(f"**Headings Structure:** H1: {report['metrics']['headings']['h1']} | H2: {report['metrics']['headings']['h2']}")
            
        with tab3:
            st.subheader("Search Engine Result Preview")
            sv = report["search_visibility"]
            st.write(f"**Query Tested:** `{sv['query_used']}`")
            if sv["ranked"]:
                st.success(f"Page appears at position **#{sv['position']}** in TinyFish Search results.")
                st.markdown(f"> **Search Snippet:** *{sv['snippet']}*")
            else:
                st.warning("Page did not appear in the top search results for this query.")
                
        with tab4:
            st.subheader("How TinyFish APIs Power This Auditor")
            st.markdown("""
            This auditor leverages two core **TinyFish** endpoints to bridge traditional SEO with the AI-first web:
            1. **TinyFish Fetch (`client.fetch.get_contents`)**: Extracts clean, AI-ready text directly from live URLs. By comparing this against raw HTML visible text, we expose client-side rendering bottlenecks that invisible AI agents and LLM scrapers miss.
            2. **TinyFish Search (`client.search.query`)**: Evaluates real-world search ranking and validates whether search engines successfully parse and snippet the target page.
            """)
else:
    st.info("👈 Enter a URL in the sidebar and click **'Run AI SEO Audit'** or select a Quick Demo Preset to begin.")