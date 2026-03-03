import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables (including GAFFA_API_KEY) from .env for local experiments.
load_dotenv()
GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")

# Explicitly fail when the API key is missing so issues surface early.
if not GAFFA_API_KEY:
    raise RuntimeError(
        "GAFFA_API_KEY is not set. Make sure it is defined in your .env file or environment."
    )


def fetch_parsed_table(url, selector="table", proxy_location=None):
    """
    Use Gaffa's `parse_table` action to extract a Wikipedia-style table.

    Parameters
    ----------
    url : str
        Page URL on Wikipedia (or any site with a similar table).
    selector : str
        CSS selector for the target table (e.g. 'table.wikitable').
    proxy_location : str | None
        Optional proxy region code for geo-sensitive content.

    Returns
    -------
    Any
        Parsed JSON payload describing the table structure.
    """
    payload = {
        "url": url,
        "proxy_location": proxy_location,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            "actions": [
                {
                    # Let Gaffa locate the table that matches `selector` and convert it to JSON.
                    "type": "parse_table",
                    "selector": selector,
                    # Wikipedia tables can be heavier; allow a slightly longer wait.
                    "timeout": 10000,
                }
            ],
        },
    }

    headers = {
        "x-api-key": GAFFA_API_KEY,
        "Content-Type": "application/json"
    }

    # Trigger a browser session in Gaffa that runs the parse_table action.
    response = requests.post(
        "https://api.gaffa.dev/v1/browser/requests",
        json=payload,
        headers=headers
    )
    response.raise_for_status()

    # The action output is a URL where the parsed table JSON can be downloaded.
    result_url = response.json()["data"]["actions"][0]["output"]
    result_response = requests.get(result_url)
    result_response.raise_for_status()

    return result_response.json()


if __name__ == "__main__":
    # This example fetches the main GDP-by-country table from Wikipedia.
    data = fetch_parsed_table(
        url="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
        selector="table.wikitable",
    )

    # Save to file
    # Persist the full parsed table to disk for offline analysis.
    with open("gdp_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Fetched {len(data)} records")
    print(json.dumps(data[:3], indent=2))
