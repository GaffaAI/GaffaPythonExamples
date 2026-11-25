# How to Scrape Twitter without Authentication

Code examples for the blog post **["A Practical Guide to Scraping Images on Pinterest: 2026 Updated"](BLOG_POST_URL)** using the [Gaffa Browser Request API](https://gaffa.dev).

The script uses Gaffa to extract publicly available data from Pinterest.

## Requirements

- Python 3.10+
- A Gaffa API key — sign up at [gaffa.dev](https://gaffa.dev) and create your key in the **API Keys** section of the dashboard

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/GaffaAI/GaffaPythonExamples.git
cd GaffaPythonExamples/scripts/ScrapePinterest
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
python pinterestscraper.py
```

Results are written to `pinterest_results.json/`.
Example:

```
      "pin": {
        "title": "Outfits",
        "description": null,
        "image_url": "https://i.pinimg.com/60x60/b7/53/56/b753566c43fd714431a0a5c7d8b4e9b5.jpg",
        "pin_url": null
``
