import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")

if not GAFFA_API_KEY:
    raise RuntimeError(
        "GAFFA_API_KEY is not set. Make sure it is defined in your .env file or environment."
    )


def fetch_dom(url, proxy_location=None):
    payload = {
        "url": url,
        "proxy_location": proxy_location,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            "actions": [
                {
                    "type": "wait",
                    "selector": "table",
                    "timeout": 5000
                },
                {
                    "type": "capture_dom"
                }
            ]
        }
    }

    headers = {
        "x-api-key": GAFFA_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.gaffa.dev/v1/browser/requests",
        json=payload,
        headers=headers
    )
    response.raise_for_status()

    dom_url = response.json()["data"]["actions"][1]["output"]
    dom_response = requests.get(dom_url)
    dom_response.raise_for_status()

    return dom_response.text


def parse_table_from_dom(html, table_selector="table"):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(table_selector)

    if not table:
        raise ValueError(f"No table found for selector: {table_selector}")

    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    rows = []

    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.select("td")]
        if cells:
            rows.append(dict(zip(headers, cells)))

    return rows


if __name__ == "__main__":
    html = fetch_dom("https://demo.gaffa.dev/simulate/table?loadTime=1&rowCount=10")
    data = parse_table_from_dom(html)

    # Print to console
    print(json.dumps(data, indent=2))

    # Save to file
    with open("table_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved {len(data)} rows to table_data.json")
