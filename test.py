from tinyfish import TinyFish

client = TinyFish()

result = client.fetch.get_contents(urls=["https://www.notion.so"])
print(result.results[0].text)