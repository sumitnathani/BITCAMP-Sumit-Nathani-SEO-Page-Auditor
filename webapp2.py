import os
from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
from tinyfish import TinyFish

app = Flask(__name__)

# Initialize TinyFish client
api_key = os.environ.get("TINYFISH_API_KEY")
client = TinyFish(api_key=api_key) if api_key else TinyFish()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DTU // AI SEO TELEMETRY ENGINE</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .accent-volt { color: #CCFF00; }
        .bg-volt { background-color: #CCFF00; }
        .border-volt { border-color: #CCFF00; }
    </style>
</head>
<body class="bg-[#050505] text-zinc-100 min-h-screen selection:bg-[#CCFF00] selection:text-black">
    <!-- Top Telemetry Bar -->
    <header class="border-b border-zinc-900 bg-[#050505] sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-2 h-2 bg-volt"></div>
                <span class="font-mono text-xs tracking-widest uppercase text-zinc-400 font-bold">DTU // LN4 TELEMETRY SYSTEM</span>
            </div>
            <div class="flex items-center gap-6 text-xs font-mono text-zinc-500">
                <span>ENGINE: TINYFISH API</span>
                <span class="text-zinc-800">|</span>
                <span class="text-zinc-300">STATUS: ACTIVE</span>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-12">
        <!-- Hero Section -->
        <div class="mb-10">
            <div class="inline-block font-mono text-[11px] tracking-widest uppercase bg-zinc-900 text-zinc-300 px-2.5 py-1 mb-3 border border-zinc-800">
                AI Search Ingestion & Ranking Audit Matrix
            </div>
            <h1 class="text-4xl font-extrabold tracking-tight text-white uppercase">PAGE READABILITY AUDITOR</h1>
            <p class="text-zinc-400 text-sm mt-2 max-w-2xl font-mono">Evaluate live web architecture against LLM scrapers and search fetch engines. Measure extraction deltas and real-world ranking visibility across varied web targets.</p>
        </div>

        <!-- Control Terminal Box -->
        <div class="bg-zinc-950 border border-zinc-800 p-6 mb-10 relative">
            <div class="absolute top-0 left-0 w-1.5 h-full bg-volt"></div>
            <form id="auditForm" onsubmit="runAudit(event)" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                    <div class="md:col-span-7">
                        <label class="block font-mono text-xs uppercase tracking-widest text-zinc-400 mb-2">Target URL</label>
                        <input type="url" id="url" required value="https://www.notion.so" class="w-full bg-black border border-zinc-800 rounded-none px-4 py-3 text-sm font-mono focus:outline-none focus:border-[#CCFF00] text-zinc-100 transition">
                    </div>
                    <div class="md:col-span-5">
                        <label class="block font-mono text-xs uppercase tracking-widest text-zinc-400 mb-2">Target Search Query</label>
                        <input type="text" id="query" value="Notion AI workspace" class="w-full bg-black border border-zinc-800 rounded-none px-4 py-3 text-sm font-mono focus:outline-none focus:border-[#CCFF00] text-zinc-100 transition">
                    </div>
                </div>
                
                <!-- Expanded Preset Matrix -->
                <div class="space-y-2 pt-2 border-t border-zinc-900">
                    <span class="block text-[11px] text-zinc-500 font-mono tracking-widest uppercase">Select Benchmark Target Preset:</span>
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                        <button type="button" onclick="loadPreset('https://www.notion.so', 'Notion AI workspace')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">1. NOTION (SPA)</button>
                        <button type="button" onclick="loadPreset('https://en.wikipedia.org/wiki/Artificial_intelligence', 'Artificial intelligence overview')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">2. WIKIPEDIA</button>
                        <button type="button" onclick="loadPreset('https://docs.stripe.com/', 'Stripe documentation API')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">3. STRIPE DOCS</button>
                        <button type="button" onclick="loadPreset('https://github.com/features/actions', 'GitHub Actions CI/CD')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">4. GITHUB ACTIONS</button>
                        <button type="button" onclick="loadPreset('https://news.ycombinator.com/', 'Hacker News tech')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">5. HACKER NEWS</button>
                        <button type="button" onclick="loadPreset('https://vercel.com/', 'Vercel frontend cloud')" class="text-[11px] font-mono bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3 py-2.5 text-zinc-300 text-left transition cursor-pointer truncate">6. VERCEL CLOUD</button>
                    </div>
                </div>

                <div class="pt-2">
                    <button type="submit" id="submitBtn" class="w-full bg-volt hover:bg-[#b3e600] text-black font-extrabold px-6 py-3.5 text-xs font-mono uppercase tracking-widest transition cursor-pointer">
                        EXECUTE AUDIT TELEMETRY
                    </button>
                </div>
            </form>
        </div>

        <!-- Loading State -->
        <div id="loading" class="hidden border border-zinc-900 bg-zinc-950 p-16 text-center my-6">
            <div class="inline-block w-6 h-6 border-2 border-zinc-800 border-t-[#CCFF00] rounded-full animate-spin mb-4"></div>
            <p class="font-mono text-xs text-zinc-400 tracking-widest uppercase">FETCHING TELEMETRY STREAMS & PARSING HTML...</p>
        </div>

        <!-- Results Workspace -->
        <div id="results" class="hidden space-y-8">
            <!-- Summary Header Card -->
            <div class="border border-zinc-800 bg-zinc-950 p-8 relative">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-zinc-900">
                    <div>
                        <h2 id="resTitle" class="text-xl font-bold text-white uppercase tracking-wide">Page Title</h2>
                        <p id="resUrl" class="font-mono text-xs text-zinc-500 mt-1.5 break-all">https://...</p>
                    </div>
                    <div id="resBadge" class="font-mono text-xs px-3 py-1.5 uppercase font-bold tracking-wider border">Status</div>
                </div>
                <p id="resDesc" class="text-zinc-400 text-sm mt-6 font-mono leading-relaxed">Meta description...</p>

                <!-- Metrics Telemetry Grid -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                    <div class="border border-zinc-900 bg-black p-4">
                        <div class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Readability Coverage</div>
                        <div id="metricCoverage" class="font-mono text-2xl font-bold mt-1 text-white">0%</div>
                    </div>
                    <div class="border border-zinc-900 bg-black p-4">
                        <div class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Raw Visible Text</div>
                        <div id="metricVisible" class="font-mono text-2xl font-bold mt-1 text-white">0 chars</div>
                    </div>
                    <div class="border border-zinc-900 bg-black p-4">
                        <div class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">AI Extracted (Fetch)</div>
                        <div id="metricFetched" class="font-mono text-2xl font-bold mt-1 text-white">0 chars</div>
                    </div>
                    <div class="border border-zinc-900 bg-black p-4">
                        <div class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Search Visibility</div>
                        <div id="metricSearch" class="font-mono text-xl font-bold mt-1 text-white">Not Ranking</div>
                    </div>
                </div>
            </div>

            <!-- Search Snippet Box -->
            <div class="border border-zinc-800 bg-zinc-950 p-6">
                <div class="font-mono text-xs uppercase tracking-widest text-zinc-400 mb-3 flex items-center justify-between">
                    <span>TinyFish Search Snippet Validation</span>
                    <span class="text-zinc-600">// RANKING INDEX</span>
                </div>
                <div id="searchSnippetBox" class="font-mono text-xs bg-black border border-zinc-900 p-4 text-zinc-300 leading-relaxed">
                    No snippet available.
                </div>
            </div>

            <!-- Issues & Fixes Log -->
            <div class="border border-zinc-800 bg-zinc-950 p-6">
                <div class="font-mono text-xs uppercase tracking-widest text-zinc-400 mb-6 flex items-center justify-between">
                    <span>Diagnostic Log & Remediation Actions</span>
                    <span id="issueCount" class="bg-zinc-900 text-zinc-300 px-2.5 py-1 font-mono text-xs border border-zinc-800">0 ISSUES</span>
                </div>
                <div id="issuesList" class="space-y-4">
                    <!-- Dynamic logs inserted here -->
                </div>
            </div>
        </div>
    </main>

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
                alert('Audit request failed: ' + err.message);
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
                badge.className = "font-mono text-xs px-3 py-1.5 uppercase font-bold tracking-wider border bg-black text-[#CCFF00] border-[#CCFF00]/40";
                badge.innerText = `READABILITY: OPTIMAL [${cov}%]`;
            } else {
                badge.className = "font-mono text-xs px-3 py-1.5 uppercase font-bold tracking-wider border bg-black text-rose-400 border-rose-500/40";
                badge.innerText = `READABILITY: CRITICAL GAP [${cov}%]`;
            }

            const sv = data.search_visibility;
            const searchEl = document.getElementById('metricSearch');
            if(sv.ranked) {
                searchEl.innerHTML = `<span class="text-[#CCFF00] font-mono">RANK #${sv.position}</span>`;
            } else {
                searchEl.innerHTML = `<span class="text-rose-400 font-mono">UNRANKED</span>`;
            }

            const snippetBox = document.getElementById('searchSnippetBox');
            if(sv.ranked && sv.snippet) {
                snippetBox.innerText = `"${sv.snippet}"`;
            } else {
                snippetBox.innerText = `Target URL absent from top search engine index for query: "${sv.query_used}".`;
            }

            const issuesContainer = document.getElementById('issuesList');
            issuesContainer.innerHTML = '';
            document.getElementById('issueCount').innerText = `${data.issues_detected.length} ISSUES DETECTED`;

            if(data.issues_detected.length === 0) {
                issuesContainer.innerHTML = `<div class="p-4 bg-black border border-zinc-900 font-mono text-xs text-[#CCFF00]">SYSTEM CHECK COMPLETE: ZERO CRITICAL DEFECTS. DOCUMENT FULLY ACCESSIBLE.</div>`;
            } else {
                data.issues_detected.forEach(issue => {
                    const isHigh = issue.severity === 'High';
                    const borderCol = isHigh ? 'border-rose-900/50 bg-rose-950/10' : 'border-zinc-800 bg-black';
                    const textCol = isHigh ? 'text-rose-400' : 'text-amber-400';
                    
                    issuesContainer.innerHTML += `
                        <div class="border ${borderCol} p-5 font-mono text-xs space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="font-bold uppercase tracking-wider ${textCol}">[SEVERITY: ${issue.severity}] // ${issue.type}</span>
                            </div>
                            <p class="text-zinc-300 font-sans text-xs"><strong>FINDING:</strong> ${issue.detail}</p>
                            <p class="text-[#CCFF00] bg-black p-3 border border-zinc-900 font-sans text-xs"><strong>REMEDIATION:</strong> ${issue.fix}</p>
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

    fetched_text = ""
    try:
        fetch_result = client.fetch.get_contents(urls=[url])
        if fetch_result.results and len(fetch_result.results) > 0:
            fetched_text = fetch_result.results[0].text
    except Exception:
        pass

    fetched_len = len(fetched_text)
    coverage_ratio = round(fetched_len / visible_len, 3) if visible_len > 0 else 0

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

    issues = []
    if coverage_ratio < 0.4:
        issues.append({
            "type": "Client-Side Rendering (JS) Bottleneck",
            "severity": "High",
            "detail": f"AI search scrapers capture only {int(coverage_ratio * 100)}% of visible text ({fetched_len:,} vs {visible_len:,} chars).",
            "fix": "Implement Server-Side Rendering (SSR) or pre-rendering protocols to expose DOM content immediately to fetch agents."
        })
    
    if not has_json_ld:
        issues.append({
            "type": "Missing Structured Data",
            "severity": "Medium",
            "detail": "No JSON-LD schema.org entity declarations located in document tree.",
            "fix": "Inject standardized schema markup to establish explicit entity relationships for AI parsing engines."
        })
        
    if headings["h1"] == 0:
        issues.append({
            "type": "Missing H1 Heading",
            "severity": "Medium",
            "detail": "No H1 heading tag detected in raw HTML structure.",
            "fix": "Ensure document contains a singular, explicit H1 heading defining core topical hierarchy."
        })
        
    if not search_ranked:
        issues.append({
            "type": "Search Visibility Gap",
            "severity": "High",
            "detail": f"Target URL absent from search index for query parameter: '{query_to_use}'.",
            "fix": "Resolve rendering and schema deficiencies to allow search algorithms to index and cite document content."
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
    print("[*] Starting LN4 Telemetry SEO Engine on http://localhost:5000")
    app.run(debug=True, port=5000)