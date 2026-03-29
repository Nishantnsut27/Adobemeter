import json
import requests

api_host = "housing-api.p.rapidapi.com"
api_endpoint = "https://housing-api.p.rapidapi.com/property/get-by-url"
api_key = "64760d4efamsh778c52d664f4989p1058e5jsnacb1fe8911a1"

target_url = "https://housing.com/in/buy/new_delhi/flat-dwarka"

headers = {
    "Content-Type": "application/json",
    "x-rapidapi-host": api_host,
    "x-rapidapi-key": api_key
}
payload = {"url": target_url}

print("testing housing.com api...")
res = requests.post(api_endpoint, json=payload, headers=headers)
print(f"status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    with open("housing_test_dump.json", "w") as f:
        json.dump(data, f, indent=2)
    print("saved to housing_test_dump.json")
else:
    print(res.text[:500])
