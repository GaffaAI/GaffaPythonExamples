import getpass
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup


PROFILE = "https://x.com/OpenAI"
LIMIT = 3
OUTPUT = Path("twitter_data")

API_KEY = (
    os.getenv("GAFFA_API_KEY")
    or getpass.getpass("Gaffa API key: ")
).strip()

if not API_KEY:
    raise SystemExit("A Gaffa API key is required.")

OUTPUT.mkdir(exist_ok=True)


def fetch_page(url, label):
    response = requests.post(
        "https://api.gaffa.dev/v1/browser/requests",
        headers={"X-API-Key": API_KEY},
        json={
            "url": url,
            "async": False,
            "proxy_location": "us",
            "settings": {
                "max_media_bandwidth": 1,
                "actions": [
                    {
                        "type": "wait",
                        "selector": "article",
                        "timeout": 15000,
                    },
                    {
                        "type": "capture_dom",
                    },
                ],
            },
        },
        timeout=90,
    )

    (OUTPUT / f"{label}.json").write_text(
        response.text,
        encoding="utf-8",
    )

    response.raise_for_status()

    body = response.json()
    data = body.get("data") or body
    actions = data.get("actions") or []

    if (
        data.get("error")
        or not actions
        or any(action.get("error") for action in actions)
    ):
        raise RuntimeError(
            f"Gaffa could not load {url}. Check {label}.json."
        )

    if not 200 <= (data.get("http_status_code") or 0) < 300:
        raise RuntimeError(
            f"X returned HTTP {data.get('http_status_code')}."
        )

    html = requests.get(
        actions[-1]["output"],
        timeout=30,
    )

    html.raise_for_status()
    html.encoding = "utf-8"

    (OUTPUT / f"{label}.html").write_text(
        html.text,
        encoding="utf-8",
    )

    return BeautifulSoup(html.text, "html.parser")


def get_count(article, label):
    element = article.select_one(
        f'[aria-label="{label}"]'
    )

    return (
        element.get_text(strip=True) or None
        if element
        else None
    )


def extract_post(soup, url):
    path = urlsplit(url).path

    stamp = soup.select_one(
        f'article a[href="{path}"]'
    )

    if stamp is None:
        raise ValueError(
            "The requested post's timestamp link is missing."
        )

    article = stamp.find_parent("article")
    body = article.select_one('div[dir="auto"]')

    handle = path.split("/")[1]
    author = None

    author_path = re.compile(
        rf"^/{re.escape(handle)}$",
        re.IGNORECASE,
    )

    for link in article.find_all(
        "a",
        href=author_path,
    ):
        if (
            link.get_text(strip=True).lower()
            == f"@{handle}".lower()
        ):
            author = link.get_text(strip=True)
            break

    if (
        author is None
        or body is None
        or not body.get_text(strip=True)
    ):
        raise ValueError(
            "The expected author or tweet text is missing."
        )

    if any(
        button.get_text(strip=True) == "Show more"
        for button in body.select("button")
    ):
        raise ValueError(
            "The tweet text is still truncated."
        )

    post_id = path.rsplit("/", 1)[-1]

    published = datetime.fromtimestamp(
        ((int(post_id) >> 22) + 1288834974657) / 1000,
        timezone.utc,
    )

    return {
        "post_id": post_id,
        "url": url,
        "author": author,
        "published_at": published.isoformat(
            timespec="seconds"
        ),
        "text": body.get_text(" ", strip=True),
        "links": [
            link["href"]
            for link in body.select(
                'a[href^="https://"]'
            )
        ],
        "likes_display": get_count(
            article,
            "Like",
        ),
        "reposts_display": get_count(
            article,
            "Repost",
        ),
        "replies_display": get_count(
            article,
            "Reply",
        ),
    }


profile = fetch_page(
    PROFILE,
    "profile",
)

profile_path = urlsplit(
    PROFILE
).path.rstrip("/")

pattern = re.compile(
    rf"^{re.escape(profile_path)}/status/\d+$",
    re.IGNORECASE,
)

urls = []

for article in profile.select("article"):
    link = article.find(
        "a",
        href=pattern,
    )

    if link:
        url = "https://x.com" + link["href"]

        if url not in urls:
            urls.append(url)

urls = urls[:LIMIT]

if not urls:
    raise RuntimeError(
        "No tweet links found. "
        "Check twitter_data/profile.html."
    )

print(f"Found {len(urls)} tweet URLs.")


posts = []
failures = []

for url in urls:
    post_id = url.rsplit("/", 1)[-1]

    try:
        soup = fetch_page(
            url,
            post_id,
        )

        post = extract_post(
            soup,
            url,
        )

        posts.append(post)

        print(
            f"Extracted tweet {post_id}."
        )

    except (
        requests.RequestException,
        ValueError,
        RuntimeError,
        KeyError,
    ) as error:
        failures.append({
            "url": url,
            "error": str(error),
        })

        print(
            f"Could not extract {url}: {error}"
        )


posts.sort(
    key=lambda post: post["published_at"],
    reverse=True,
)

(OUTPUT / "posts.json").write_text(
    json.dumps(
        posts,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

(OUTPUT / "failures.json").write_text(
    json.dumps(
        failures,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print(
    f"Saved {len(posts)} tweets; "
    f"{len(failures)} failed."
)

if not posts:
    raise SystemExit(
        "No tweets extracted. "
        "Check twitter_data/failures.json."
    )

