import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")

if not GAFFA_API_KEY:
    raise RuntimeError(
        "GAFFA_API_KEY is not set. Make sure it is defined in your .env file or environment."
    )


def fetch_parsed_table(url, selector="table", proxy_location=None):
    payload = {
        "url": url,
        "proxy_location": proxy_location,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            "actions": [
                {
                    "type": "parse_table",
                    "selector": selector,
                    "timeout": 5000
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

    result_url = response.json()["data"]["actions"][0]["output"]
    result_response = requests.get(result_url)
    result_response.raise_for_status()

    return result_response.json()


if __name__ == "__main__":
    data = fetch_parsed_table(
        url="https://demo.gaffa.dev/simulate/table?loadTime=1&rowCount=10"
    )

    # Print to console
    print(json.dumps(data, indent=2))
