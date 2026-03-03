# Gaffa Table Scraper

Code examples for the blog post **"How to Scrape a Table with Python (The Easy Way)"** using the [Gaffa Browser Request API](https://gaffa.dev).

## Files

| File | Description |
|---|---|
| `capture_dom.py` | Fetches raw HTML DOM via Gaffa and parses the table locally with BeautifulSoup |
| `parse_table_demo.py` | Uses Gaffa's `parse_table` action on the Gaffa demo site — returns JSON directly with no processing |
| `parse_table_wikipedia.py` | Uses Gaffa's `parse_table` action on Wikipedia's GDP by Country table — real-world example |

## Requirements

- Python 3.8+
- A Gaffa API key — sign up at [gaffa.dev](https://gaffa.dev) and create your key in the **API Keys** section of the dashboard

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/GaffaAI/GaffaPythonExamples.git
cd scraping-tables
```

**2. Install dependencies**
```bash
pip install requests beautifulsoup4 python-dotenv
```

**3. Add your API key**

Create a `.env` file in the root of the project:
```bash
GAFFA_API_KEY=your_key_here
```

## Usage

**Capture DOM + BeautifulSoup (Approach 1)**
```bash
python capture_dom.py
```
Fetches the Gaffa demo table as raw HTML and parses it with BeautifulSoup. Outputs the data to the console and saves it to `table_data.json`.

---

**parse_table on the demo site (Approach 2 — basic)**
```bash
python parse_table_demo.py
```
Uses Gaffa's `parse_table` action to fetch and parse the demo table in one step. No BeautifulSoup needed. Prints the JSON output to the console.

---

**parse_table on Wikipedia (Approach 2 — real-world)**
```bash
python parse_table_wikipedia.py
```
Uses Gaffa's `parse_table` action on Wikipedia's List of Countries by GDP (Nominal). Saves the output to `gdp_data.json` and prints a preview of the first 3 records.

## Sample Output

`parse_table_wikipedia.py` returns data like this:

```json
[
  {
    "country_territory": "World",
    "imf__2026__1": "123,584,494",
    "world_bank__2024__6": "111,326,370",
    "united_nations__2024__7": "100,834,796"
  },
  {
    "country_territory": "United States",
    "imf__2026__1": "31,821,293",
    "world_bank__2024__6": "28,750,956",
    "united_nations__2024__7": "29,298,000"
  }
]
```

Column headers are automatically normalised by Gaffa — lowercased and special characters replaced with underscores.

## Notes

- For sites that require proxy access or restrict by geography, add `proxy_location="us"` (or any supported region) to route the request through the appropriate IP.
- All JSON output files (`table_data.json`, `gdp_data.json`) are saved to the `output/` folder.