import requests
from bs4 import BeautifulSoup

raw_html = requests.get("https://www.notion.so", headers={
    "User-Agent": "Mozilla/5.0"
}).text

soup = BeautifulSoup(raw_html, "html.parser")

# Remove script/style tags so we're measuring real visible text, not JS code
for tag in soup(["script", "style"]):
    tag.decompose()

visible_text = soup.get_text(separator=" ", strip=True)
print("VISIBLE TEXT LENGTH (after stripping scripts):", len(visible_text))
print(visible_text[:500])