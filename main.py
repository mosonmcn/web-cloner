import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup 

# Shigo da ma'aikata daga folder mon/
from mon.fetcher import fetch
from mon.filesystem import path_to_local
from mon.saver import save_content
from mon.parser import extract_paths
from mon.api_analyzer import advanced_static_analysis, save_api_spec
from mon.explorer import generate_website_explorer

domain = "payfluxai.com.ng"
base_url = "https://" + domain

def get_unique_domain_folder(base_domain):
    """
    Injin dake duba folder: Idan akwai data/payfluxai.com.ng,
    zai kera data/payfluxai.com.ng_2, data/payfluxai.com.ng_3, da sauransu.
    """
    target_folder = os.path.join("data", base_domain)
    if not os.path.exists(target_folder):
        return base_domain, target_folder
        
    counter = 2
    while True:
        new_domain_name = f"{base_domain}_{counter}"
        new_folder = os.path.join("data", new_domain_name)
        if not os.path.exists(new_folder):
            return new_domain_name, new_folder
        counter += 1

# Kaddamar da gano folder ta musamman
active_domain_name, output_folder_path = get_unique_domain_folder(domain)

visited = set()
queue = ["/"]

print(f"[+] Launching Ultra-Duty AI Reverse Engine for -> {base_url}")
print(f"[+] Local Repository root set to: {output_folder_path}\n")

while queue:
    path = queue.pop(0)
    if path in visited:
        continue
        
    full_url = urljoin(base_url, path)
    print(f"[📥 FETCHING] -> {full_url}")
    visited.add(path)
    
    status, content, ctype = fetch(full_url)
    if status != 200:
        print(f"   [❌ FAILED] HTTP status code {status}")
        continue
        
    # Sanya sunan file da madaidacin tafarki na gida
    local_file_path = path_to_local(active_domain_name, path, ctype)
    
    # Ajiye danyen bayani (HTML, JS, CSS, hotuna ko videos)
    save_content(local_file_path, content)
    
    # --- CYBER THREAT INTELLIGENCE & API REVERSE SECTION ---
    # MATAKI NA A: IDAN FAYIL DIN JAVASCRIPT NE
    if ctype and ("javascript" in ctype or "x-javascript" in ctype) or path.endswith(".js"):
        print(f"   [⚙️ STATIC ANALYSIS] Scanning JavaScript functions inside: /{path}...")
        discovered_specs = advanced_static_analysis(content, current_file_route=f"/{path.lstrip('/')}")
        if discovered_specs:
            save_api_spec(active_domain_name, discovered_specs)

    # MATAKI NA B: IDAN SHAFIN HTML NE
    if ctype and "text/html" in ctype:
        soup = BeautifulSoup(content, "html.parser")
        
        inline_scripts = soup.find_all("script")
        for script in inline_scripts:
            if script.string and ("apiCall" in script.string or "fetch" in script.string):
                print(f"   [🔍 INLINE SCRIPT] Found potential API logic inside HTML layout!")
                html_discovered_specs = advanced_static_analysis(script.string, current_file_route=f"/{path.lstrip('/')}")
                if html_discovered_specs:
                    save_api_spec(active_domain_name, html_discovered_specs)

        # Ci gaba da kwaso sauran hanyoyin HTML
        new_paths = extract_paths(content, full_url, domain)
        for p in new_paths:
            if p not in visited: 
                queue.append(p)

# Kaddamar da gina babban Explorer Tree a daidai sabuwar folder din
print(f"\n[+] Mapping cloned directory structure for {active_domain_name}...")
generate_website_explorer(active_domain_name)

print(f"\n[🎯 SYSTEM COMPLETE] Full-Stack extraction finished!")
print(f"   -> Frontend files saved in: {output_folder_path}")
print(f"   -> API Specification Model compiled in: data/{active_domain_name}/api_spec.json\n")