import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_paths(html_or_js_content, current_url, domain):
    """
    Universal Link Scanner: Yana ciro hanyoyin sadarwa daga HTML links,
    kuma yana shiga cikin JS code don zakulo window.location ko redirect paths.
    """
    discovered_paths = set()
    
    # Kariya: Tabbatar da cewa muna da rubutu (string)
    if isinstance(html_or_js_content, bytes):
        try:
            content_str = html_or_js_content.decode('utf-8', errors='ignore')
        except Exception:
            return []
    else:
        content_str = html_or_js_content

    # --- SASHEN NA 1: FARAUTAR LINKS A CIKIN HTML (<a href="...">) ---
    try:
        soup = BeautifulSoup(content_str, "html.parser")
        for tag in soup.find_all(["a", "link", "script", "img", "iframe"], href=True):
            href = tag.get("href")
            if href:
                _process_raw_link(href, current_url, domain, discovered_paths)
        for tag in soup.find_all(["script", "img", "iframe", "source"], src=True):
            src = tag.get("src")
            if src:
                _process_raw_link(src, current_url, domain, discovered_paths)
    except Exception:
        pass  # Idan ba HTML bane (fayil din JS ne na tsawa), mu tsallake zuwa Regex

    # --- SASHEN NA 2: UNIVERSAL JS ROUTER LINK SCANNER (Mafi Karfi) ---
    # Wannan regex din zai farauto kowane irin window.location.href, location.replace, ko danyen kiran kusa
    js_patterns = [
        r'(?:window\.)?location(?:\.href)?\s*=\s*[\'"`]([^\'"`]+)[\'"`]',
        r'(?:window\.)?location\.replace\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        r'(?:window\.)?location\.assign\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)',
        r'href\s*:\s*[\'"`](/[^\'"`]+)[\'"`]',  # Routers na JS kamar Vue/React paths
        r'url\s*:\s*[\'"`](/[^\'"`]+)[\'"`]'
    ]
    
    for pattern in js_patterns:
        js_links = re.findall(pattern, content_str)
        for link in js_links:
            # Tace datti idan lamba ko abun da bai dace ba ya fito
            if link and not link.startswith("http") and ("." in link or "/" in link or len(link) > 3):
                _process_raw_link(link, current_url, domain, discovered_paths)

    return list(discovered_paths)

def _process_raw_link(raw_link, current_url, domain, path_set):
    """
    Ma'aikaci na sirri dake tantance domain da kuma tabbatar da tsabtar tafarki.
    """
    # Cire datti na karshe ko space
    raw_link = raw_link.strip()
    
    # Cire javascript:void(0) ko makamancinsu
    if raw_link.lower().startswith("javascript:") or raw_link.startswith("#"):
        return

    # Hada hanyar da asalin inda muke (urljoin yana warware ../ kamar browser)
    absolute_url = urljoin(current_url, raw_link)
    parsed_url = urlparse(absolute_url)

    # Tabbatar da cewa hanyar ta cikin gidan website dinmu ne kadai, ba ta waje ba
    if parsed_url.netloc == domain or parsed_url.netloc == f"www.{domain}":
        clean_path = parsed_url.path
        
        # Idan shafin bashi da suna a karshe amma directory ne, tabbatar ya kare da "/"
        if not clean_path:
            clean_path = "/"
            
        path_set.add(clean_path)
