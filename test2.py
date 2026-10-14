import requests

raw_html = requests.get("https://www.notion.so", headers={
    "User-Agent": "Mozilla/5.0"
}).text

print("RAW HTML LENGTH:", len(raw_html))