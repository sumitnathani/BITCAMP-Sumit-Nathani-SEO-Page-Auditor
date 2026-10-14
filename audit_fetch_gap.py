import requests
from bs4 import BeautifulSoup
from tinyfish import TinyFish

client = TinyFish()

def audit_fetch_coverage(url):
    # Raw HTML -> visible text
    raw_html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    visible_text = soup.get_text(separator=" ", strip=True)

    # TinyFish Fetch extraction
    result = client.fetch.get_contents(urls=[url])
    if result.errors:
        return {"url": url, "status": "fetch_blocked", "error": result.errors[0].error}

    fetched_text = result.results[0].text

    coverage_ratio = len(fetched_text) / len(visible_text) if visible_text else 0

    return {
        "url": url,
        "visible_text_length": len(visible_text),
        "fetched_text_length": len(fetched_text),
        "coverage_ratio": round(coverage_ratio, 3),
        "status": "ok"
    }

if __name__ == "__main__":
    for test_url in ["https://en.wikipedia.org/wiki/Artificial_intelligence", "https://www.notion.so"]:
        print(audit_fetch_coverage(test_url))