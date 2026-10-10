# How to Scrape Twitter without Authentication

Code examples for the blog post **["How to Scrape Twitter without Authentication: Gaffa Guide"](BLOG_POST_URL)** using the [Gaffa Browser Request API](https://gaffa.dev).

The script loads a public X profile with Gaffa's `capture_dom` action, finds the visible tweet links, and saves each post's text, publish time, links, and engagement counts as JSON. No X account or login is needed.

## Requirements

- Python 3.10+
- A Gaffa API key — sign up at [gaffa.dev](https://gaffa.dev) and create your key in the **API Keys** section of the dashboard

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/GaffaAI/GaffaPythonExamples.git
cd GaffaPythonExamples/scripts/ScrapeX
```

**2. Install dependencies**
```bash
pip install requests beautifulsoup4
```

**3. Add your API key**

Set it as an environment variable:
```bash
export GAFFA_API_KEY=your_key_here
```
If it isn't set, the script will prompt you for it when it runs.

## Run

```bash
python xscraper.py
```

Results are written to `twitter_data/`:

- `posts.json` — the extracted tweets, newest first
- `failures.json` — any tweet URLs that couldn't be extracted, with the error
- `*.json` / `*.html` — the raw Gaffa response and captured HTML for each page, useful for debugging

To scrape a different account, change `PROFILE` in `xscraper.py`. `LIMIT` caps how many tweets are processed, but signed-out profiles usually only show a few posts.
