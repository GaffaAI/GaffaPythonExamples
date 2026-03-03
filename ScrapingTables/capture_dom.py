import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables (including GAFFA_API_KEY) from a local .env file if present.
load_dotenv()
GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")

# Fail fast when the API key is missing so callers get a clear, actionable error.
if not GAFFA_API_KEY:
    raise RuntimeError(
        "GAFFA_API_KEY is not set. Make sure it is defined in your .env file or environment."
    )


def fetch_dom(url, proxy_location=None):
    """
    Request a rendered page from Gaffa and capture its full DOM.

    The browser session waits until a <table> element is present before
    capturing the DOM snapshot, which improves reliability for pages that
    render tables asynchronously.

    Parameters
    ----------
    url : str
        Page URL to render in the Gaffa browser.
    proxy_location : str | None
        Optional proxy region code. Leave as None to use the default location.

    Returns
    -------
    str
        Raw HTML string representing the captured DOM.
    """
    payload = {
        "url": url,
        "proxy_location": proxy_location,
        "async": False,
        "max_cache_age": 0,
        "settings": {
            "record_request": False,
            # Action pipeline executed in the remote browser.
            "actions": [
                {
                    # Wait until at least one <table> is present in the DOM
                    # (or until the timeout elapses) so that we do not capture
                    # an empty or partially rendered page.
                    "type": "wait",
                    "selector": "table",
                    "timeout": 5000,
                },
                {
                    # Downloadable snapshot of the full DOM once the wait step completes.
                    "type": "capture_dom",
                },
            ]
        }
    }

    headers = {
        "x-api-key": GAFFA_API_KEY,
        "Content-Type": "application/json"
    }

    # Create a new browser request in Gaffa; this returns metadata and action outputs.
    response = requests.post(
        "https://api.gaffa.dev/v1/browser/requests",
        json=payload,
        headers=headers
    )
    response.raise_for_status()

    # The capture_dom action exposes a signed URL where the HTML snapshot can be fetched.
    dom_url = response.json()["data"]["actions"][1]["output"]
    dom_response = requests.get(dom_url)
    dom_response.raise_for_status()

    return dom_response.text


def parse_table_from_dom(html, table_selector="table"):
    """
    Extract a table from an HTML document into a list of row dicts.

    Parameters
    ----------
    html : str
        HTML source that contains the table markup.
    table_selector : str
        CSS selector that identifies the target table (defaults to the first <table>).

    Returns
    -------
    list[dict[str, str]]
        One dictionary per table row, keyed by header text.

    Raises
    ------
    ValueError
        If no table matching the selector is found.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(table_selector)

    if not table:
        raise ValueError(f"No table found for selector: {table_selector}")

    # Build header labels from the table's <thead>. These become dict keys for each row.
    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    rows = []

    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.select("td")]
        if cells:
            # Map each cell to the corresponding column header.
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
