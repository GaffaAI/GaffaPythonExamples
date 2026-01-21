import os
import re
import requests
from urllib.parse import urljoin

GAFFA_API_KEY = os.getenv("GAFFA_API_KEY")
HEADERS = {
    "x-api-key": GAFFA_API_KEY,
    "Content-Type": "application/json"
}

def get_sitemap_urls(site_url, max_cache_age=86400):
    payload = {
        "url": site_url,
        "max_cache_age": max_cache_age
    }
    print("Retrieving sitemap URLs.")
    response = requests.post("https://api.gaffa.dev/v1/site/map", json=payload, headers=HEADERS)
    return response.json()["data"]["links"]

def get_dom(url):
    payload = {
        "url": url,
        "async": False,
        "settings": {
            "actions": [
                {"type": "wait", "selector": "img", "timeout": 20000},
                {"type": "capture_dom"}
            ],
            "time_limit": 40000
        }
    }
    print("Capturing DOM URL.")
    response = requests.post("https://api.gaffa.dev/v1/browser/requests", json=payload, headers=HEADERS)
    dom_url = response.json()["data"]["actions"][1]["output"]
    print("Retrieving DOM.")
    dom_response = requests.get(dom_url)
    return dom_response.text

def extract_image_urls(dom_content, base_url):
    image_urls = []
    src_pattern = r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']'
    matches = re.findall(src_pattern, dom_content)
    
    for src in matches:
        if not src.startswith(('http:', 'https:')):
            src = urljoin(base_url, src)
        image_urls.append(src)
    
    return image_urls

def download_image(image_url, filename):
    payload = {
        "url": image_url,
        "async": False,
        "settings": {
            "actions": [{"type": "download_file"}]
        }
    }
    print("Retrieving download URL.")
    response = requests.post("https://api.gaffa.dev/v1/browser/requests", json=payload, headers=HEADERS)
    actions = response.json()["data"]["actions"]
    download_url = actions[0]["output"]
    download_ext = os.path.splitext(download_url)[1]
    
    print("Downloading image.")
    img_response = requests.get(download_url)
    filepath = f"{filename}{download_ext}"
    with open(filepath, 'wb') as f:
        f.write(img_response.content)

def main():
    site_url = "https://gaffa.dev"
    sitemap_urls = get_sitemap_urls(site_url)[:3]
    
    for i, url in enumerate(sitemap_urls, 1):
        dom_content = get_dom(url)
        image_urls = extract_image_urls(dom_content, url)
        
        if image_urls:
            download_image(image_urls[0], f"image_{i}")

if __name__ == "__main__":
    main()