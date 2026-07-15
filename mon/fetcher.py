import requests
from urllib.parse import urljoin, urlparse

# Headers masu karfi na boye ma'aikata
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

def fetch(url):
    """
    Yana kwaso shafukan yanar gizo kuma yana dawo da abubuwa guda uku:
    Status Code, Danyen Rubutu (HTML/JS), da kuma Content-Type.
    """
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Dauko content-type din daga server (misali text/html ko application/javascript)
        content_type = r.headers.get("Content-Type", "").lower()
        return r.status_code, r.text, content_type
    except Exception as e:
        return 500, str(e), "failed"
