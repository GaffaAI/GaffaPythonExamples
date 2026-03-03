import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables (including GAFFA_API_KEY) from .env for local runs.
load_dotenv()
GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")

# Ensure callers get a clear error message instead of subtle auth failures.
if not GAFFA_API_KEY:
    raise RuntimeError(
        "GAFFA_API_KEY is not set. Make sure it is defined in your .env file or environment."
    )


def fetch_parsed_table(url, selector="table", proxy_location=None):
    """
    Ask Gaffa to locate and parse an HTML table into structured JSON.

    This uses the `parse_table` browser action, which runs in a real browser
    context and returns a downloadable JSON representation of the table.

    Parameters
    ----------
    url : str
        Page URL that contains the target table.
    selector : str
        CSS selector for the table element to parse.
    proxy_location : str | None
        Optional proxy region code. Leave as None for the default.

    Returns
    -------
    Any
        Parsed JSON payload describing the table (rows, headers, etc.).
    """
    payload = {
        "url": url,
        "proxy_location": proxy_location,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            # Single-action workflow: find the table and return its parsed contents.
            "actions": [
                {
                    "type": "parse_table",
                    "selector": selector,
                    # Upper bound on how long we wait for the table to be present.
                    "timeout": 5000,
                }
            ],
        },
    }

    headers = {
        "x-api-key": GAFFA_API_KEY,
        "Content-Type": "application/json"
    }

    # Create a browser request in Gaffa; the parse_table action will produce a result URL.
    response = requests.post(
        "https://api.gaffa.dev/v1/browser/requests",
        json=payload,
        headers=headers
    )
    response.raise_for_status()

    # The parse_table action returns a signed URL to the parsed table JSON.
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
