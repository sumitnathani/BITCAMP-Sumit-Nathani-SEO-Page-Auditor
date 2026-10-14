from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
from tinyfish import TinyFish

app = Flask(__name__)
client = TinyFish()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTU: AI SEO Page Auditor</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
    <div class="max-w-5xl mx-auto px-4 py-10">
        <!-- Header -->
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-800 pb-6 mb-8 gap-4">
            <div>
                <span class="bg-indigo-500/10 text-indigo-400 text-xs font-semibold px-3 py-1 rounded-full border border-indigo-500/20">TinyFish × DTU Workshop</span>
                <h1 class="text-3xl font-bold tracking-tight mt-2 text-white">AI SEO Page Auditor</h1>
                <p class="text-slate-400 text-sm mt-1">Audit whether AI search & fetch tools can read, understand, and rank your web pages.</p>
            </div>
            <div class="flex gap-2">
                <button onclick="loadPreset('https://www.notion.so', 'Notion AI workspace')" class="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-2 rounded-lg transition text-slate-300 cursor-pointer">Test Notion (SPA)</button>
                <button onclick="loadPreset('https://en.wikipedia.org/wiki/Artificial_intelligence', 'Artificial intelligence overview')" class="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-2 rounded-lg transition text-slate-300 cursor-pointer">Test Wikipedia</button>
            </div>
        </div>

        <!-- Input Form -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8 shadow-xl">
            <form id="auditForm" onsubmit="runAudit(event)" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1">Target URL</label>
                        <input type="url" id="url" required value="https://www.notion.so" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 text-slate-200">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-400 mb-1">Target Search Query (Optional)</label>
                        <input type="text" id="query" value="Notion AI workspace" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 text-slate-200">
                    </div>
                </div>
                <button type="submit" id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-500 font-medium py-3 rounded-xl transition text-sm shadow-lg shadow-indigo-600/20 cursor-pointer flex items-center justify-center gap-2">
                    <span>Run AI SEO Audit</span>
                </button>
            </form>
        </div>

        <!-- Loading State -->
        <div id="loading" class="hidden text-center py-20">
            <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent mb-4"></div>
            <p class="text-slate-400 text-sm">Analyzing live page with TinyFish Fetch & Search APIs...</p>
        </div>

        <!-- Results Section -->
        <div id="results" class="hidden space-y-6">
            <!-- Overview Card -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4 mb-6">
                    <div>
                        <h2 id="resTitle" class="text-xl font-bold text-white">Page Title</h2>
                        <p id="resUrl" class="text-xs text-indigo-400 mt-0.5 break-all">https://...</p>
                    </div>
                    <span id="resBadge" class="px-3 py-1 rounded-full text-xs font-semibold">Score</span>
                </div>
                <p id="resDesc" class="text-slate-400 text-sm mb-6">Meta description goes here...</p>

                <!-- Metrics Grid -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <div class="text-xs text-slate-400">AI Readability</div>
                        <div id="metricCoverage" class="text-2xl font-bold mt-1 text-white">0%</div>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <div class="text-xs text-slate-400">Raw Visible Text</div>
                        <div id="metricVisible" class="text-2xl font-bold mt-1 text-white">0 chars</div>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <div class="text-xs text-slate-400">TinyFish Extracted</div>
                        <div id="metricFetched" class="text-2xl font-bold mt-1 text-white">0 chars</div>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                        <div class="text-xs text-slate-400">Search Visibility</div>
                        <div id="metricSearch" class="text-xl font-bold mt-1 text-white">Not Ranking</div>
                    </div>
                </div>
            </div>

            <!-- Search Snippet -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h3 class="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">🔍 TinyFish Search Result Preview</h3>
                <div id="searchSnippetBox" class="bg-slate-950 border border-slate-800 p-4 rounded-xl text-sm text-slate-300 italic">No search result preview available.</div>
            </div>

            <!-- Issues & Fixes -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h3 class="text-sm font-semibold text-slate-300 mb-4">🚨 Actionable AI-SEO Issues & Fixes</h3>
                <div id="issuesList" class="space-y-4">
                    <!-- Injected via JS -->
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadPreset(url, query) {
            document.getElementById('url').value = url;
            document.getElementById('query').value = query;
        }

        async function runAudit(e) {
            e.preventDefault();
            const url = document.getElementById('url').value;
            const query = document.getElementById('query').value;

            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');

            try {
                const response = await fetch('/api/audit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, query })
                });
                const data = await response.json();
                
                if(data.error) {
                    alert(data.error);
                    return;
                }

                renderResults(data);
            } catch(err) {
                alert('Audit failed: ' + err.message);
            } finally {
                document.getElementById('loading').classList.add('hidden');
            }
        }

        function renderResults(data) {
            document.getElementById('resTitle').innerText = data.page_title;
            document.getElementById('resUrl').innerText = data.url;
            document.getElementById('resDesc').innerText = data.meta_description;

            const cov = Math.round(data.metrics.coverage_ratio * 100);
            document.getElementById('metricCoverage').innerText = cov + '%';
            document.getElementById('metricVisible').innerText = data.metrics.visible_text_length.toLocaleString() + ' chars';
            document.getElementById('metricFetched').innerText = data.metrics.fetched_text_length.toLocaleString() + ' chars';

            const badge = document.getElementById('resBadge');
            if(cov > 40) {
                badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                badge.innerText = "High Readability (" + cov + "%)";
            } else {
                badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20";
                badge.innerText = "Critical JS Render Gap (" + cov + "%)";
            }

            const sv = data.search_visibility;
            const searchEl = document.getElementById('metricSearch');
            if(sv.ranked) {
                searchEl.innerHTML = `<span class="text-emerald-400 text-base">Ranked #${sv.position}</span>`;
            } else {
                searchEl.innerHTML = `<span class="text-rose-400 text-base">Not Ranking</span>`;
            }

            const snippetBox = document.getElementById('searchSnippetBox');
            if(sv.ranked && sv.snippet) {
                snippetBox.innerText = `"${sv.snippet}"`;
            } else {
                snippetBox.innerText = `Page did not appear in top search engine results for query: "${sv.query_used}".`;
            }

            const issuesContainer = document.getElementById('issuesList');
            issuesContainer.innerHTML = '';
            if(data.issues_detected.length === 0) {
                issuesContainer.innerHTML = `<div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm">✔ No critical AI-readability or visibility issues detected!</div>`;
            } else {
                data.issues_detected.forEach(issue => {
                    const isHigh = issue.severity === 'High';
                    const borderCol = isHigh ? 'border-rose-500/30 bg-rose-500/5' : 'border-amber-500/30 bg-amber-500/5';
                    const textCol = isHigh ? 'text-rose-400' : 'text-amber-400';
                    
                    issuesContainer.innerHTML += `
                        <div class="border ${borderCol} p-4 rounded-xl space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold uppercase tracking-wider ${textCol}">${issue.severity} Severity — ${issue.type}</span>
                            </div>
                            <p class="text-sm text-slate-300"><strong>Finding:</strong> ${issue.detail}</p>
                            <p class="text-sm text-indigo-300 bg-indigo-950/40 p-3 rounded-lg border border-indigo-500/20">💡 <strong>Recommended Fix:</strong> ${issue.fix}</p>
                        </div>
                    `;
                });
            }

            document.getElementById('results').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/audit', methods=['POST'])
def api_audit():
    req = request.get_json()
    url = req.get('url')
    target_query = req.get('query')

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
        return jsonify({"error": f"Failed to parse raw HTML: {str(e)}"}), 400

    # 2. TinyFish Fetch Coverage
    fetched_text = ""
    try:
        fetch_result = client.fetch.get_contents(urls=[url])
        if fetch_result.results and len(fetch_result.results) > 0:
            fetched_text = fetch_result.results[0].text
    except Exception:
        pass

    fetched_len = len(fetched_text)
    coverage_ratio = round(fetched_len / visible_len, 3) if visible_len > 0 else 0

    # 3. TinyFish Search Visibility Check
    query_to_use = target_query or page_title
    search_ranked = False
    search_position = None
    search_snippet = None
    
    try:
        search_result = client.search.query(query=query_to_use, location="IN", language="en")
        if search_result and hasattr(search_result, 'results'):
            for idx, item in enumerate(search_result.results, start=1):
                if url.lower() in item.url.lower():
                    search_ranked = True
                    search_position = idx
                    search_snippet = item.snippet
                    break
    except Exception:
        pass

    # 4. Synthesize Issues
    issues = []
    if coverage_ratio < 0.4:
        issues.append({
            "type": "Client-Side Rendering Bottleneck",
            "severity": "High",
            "detail": f"AI tools see only {int(coverage_ratio * 100)}% of visible page content ({fetched_len:,} vs {visible_len:,} chars).",
            "fix": "Implement Server-Side Rendering (SSR) or pre-rendering so crawlers and AI bots can read text immediately."
        })
    
    if not has_json_ld:
        issues.append({
            "type": "Missing Structured Data",
            "severity": "Medium",
            "detail": "No JSON-LD schema.org blocks found on the page.",
            "fix": "Add relevant schema markup (Article, Product, Organization) to help AI search engines understand entities."
        })
        
    if headings["h1"] == 0:
        issues.append({
            "type": "Missing H1 Heading",
            "severity": "Medium",
            "detail": "No H1 heading tag found in raw markup.",
            "fix": "Ensure every page has a single clear H1 tag summarizing the core topic for AI summarizers."
        })
        
    if not search_ranked:
        issues.append({
            "type": "Search Visibility Gap",
            "severity": "High",
            "detail": f"Page is not currently ranking in top search results for query: '{query_to_use}'.",
            "fix": "Address rendering and structural gaps above to ensure search engines can successfully index and cite your content."
        })

    return jsonify({
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
    })

if __name__ == '__main__':
    print("[*] Starting AI SEO Auditor Web Server on http://localhost:5000")
    app.run(debug=True, port=5000)