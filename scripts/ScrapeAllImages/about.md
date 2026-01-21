# Automatically Scrape Every Image from a Website

This folder contains a Python script that demonstrates how to use Gaffa's [Site Mapping](https://gaffa.dev/docs/features/mapping-requests) and [Browser Requests](https://gaffa.dev/docs/features/browser-requests/actions/download-file) APIs to automatically scrape and download every image from a website.

## What It Does

1. **Maps the Territory**: Uses Gaffa's `site/map` endpoint to find every page on the target website
2. **Renders Each Page**: Uses Gaffa's [Browser Request API](https://gaffa.dev/docs/features/browser-requests) to capture the fully-rendered DOM (including JavaScript-loaded images)
3. **Finds & Downloads**: Extracts all `<img>` tags and downloads the images using Gaffa's [`download_file`](https://gaffa.dev/docs/features/browser-requests/actions/download-file) action

## How to Run

First, make sure you have the required libraries installed and your `GAFFA_API_KEY` environment variable set.

Required libraries:

```bash
pip install requests
```

Then, run the script:

```bash
python scrape_images.py
```

## Why Use Gaffa for This?

- **Handles JavaScript**: Modern sites load images dynamically — Gaffa renders the full page first
- **Stealth & Success**: [Residential proxies](https://gaffa.dev/blog/simplify-your-web-automation-with-rotating-residential-proxies-in-gaffa) and real browser fingerprints make requests appear as legitimate user traffic
- **Responsible Caching**: With `max_cache_age`, repeated requests are served from cache, sparing target servers
- **Built-in Reliability**: Automatic request pacing and retries (always respect `robots.txt`)
- **Automatic Format Detection**: Correct file extension provided in the download URL — no content-type parsing needed

For more information, see the [Gaffa documentation](https://gaffa.dev/docs).
