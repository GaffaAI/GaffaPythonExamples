
import json
import requests
from pathlib import Path
from mimetypes import guess_extension
from urllib.parse import quote

API_KEY = ""

QUERY = "men business casual"
OUTPUT_DIR = Path("pinterest_images")
JSON_FILE = Path("pinterest_results.json")
API_URL = "https://api.gaffa.dev/v1/browser/requests"


def field(name, description, field_type="string", fields=None):
    result = {"type": field_type, "name": name, "description": description}
    if fields is not None:
        result["fields"] = fields
    return result


payload = {
    "url": f"https://www.pinterest.com/search/pins/?q={quote(QUERY)}",
    "async": False,
    "max_cache_age": 0,
    "settings": {
        "record_request": False,
        "actions": [
            {"type": "wait", "time": 5000},
            {"type": "scroll", "percentage": 100, "scroll_speed": "slow",
             "interval": 1000, "wait_time": 1500, "max_scroll_time": 15000},
            {
                "type": "parse_json",
                "model": "gpt-4o-mini",
                "output_type": "inline",
                "input_token_cap": 30000,
                "instruction": "Extract up to 20 visible Pinterest pins. Do not invent URLs. Image URLs must be direct image URLs, not pin page URLs. Return null for missing fields.",
                "data_schema": {
                    "name": "PinterestSearchResults",
                    "description": "Pinterest search results.",
                    "fields": [
                        field("query", "Search query."),
                        field("pins", "Pinterest search results.", "array", [
                            field("pin", "One pin.", "object", [
                                field("title", "Pin title."),
                                field("description", "Pin description."),
                                field("image_url", "Direct pin image URL."),
                                field("pin_url", "Pinterest pin page URL."),
                            ])
                        ]),
                    ]
                }
            }
        ]
    }
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def download_image(url, index):
    if not url or not url.startswith("http"):
        return None

    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.pinterest.com/",
        }, timeout=30)
        response.raise_for_status()

        extension = guess_extension(
            response.headers.get("Content-Type", "").split(";")[0]
        ) or ".jpg"
        filepath = OUTPUT_DIR / f"pin_{index}{extension}"
        filepath.write_bytes(response.content)
        return str(filepath)
    except requests.RequestException as error:
        print(f"Image {index} download failed: {error}")
        return None


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Searching Pinterest: {QUERY}")

    response = requests.post(API_URL, json=payload, headers=headers, timeout=240)
    response.raise_for_status()
    result = response.json()["data"]

    if result.get("state") != "completed":
        raise RuntimeError(f"Gaffa request failed: {result.get('error_reason')}")

    parse_action = next(
        (action for action in result.get("actions", [])
         if action.get("type") == "parse_json"),
        None,
    )
    if not parse_action:
        raise RuntimeError("Gaffa did not return a parse_json action.")

    extracted = parse_action.get("output")
    if isinstance(extracted, str):
        extracted = json.loads(extracted)
    if not isinstance(extracted, dict):
        print(json.dumps(result, indent=2))
        raise RuntimeError("No inline JSON data returned.")

    pins = extracted.get("pins", [])
    for index, pin in enumerate(pins, start=1):
        pin["local_image"] = download_image(pin.get("image_url"), index)

    output = {"query": QUERY, "total_results": len(pins), "pins": pins}
    JSON_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nScraping completed!")
    print(f"Pins extracted: {len(pins)}")
    print(f"Images downloaded: {sum(bool(pin.get('local_image')) for pin in pins)}")
    print(f"JSON saved: {JSON_FILE}")
    print(f"Images saved: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
