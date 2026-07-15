import os
import json
from bs4 import BeautifulSoup

def get_html_title(file_path):
    """
    Yana bude asalin HTML file din da aka sauke domin ciro ainihin <title> dinsa.
    """
    if not os.path.exists(file_path):
        return "No Title"
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            if soup.title and soup.title.string:
                return soup.title.string.strip()
    except Exception:
        pass
    return "Untitled Page"

def generate_visual_tree(base_path, current_dir, prefix=""):
    """
    Yana gina kyakkyawan tsarin zane (Tree Chart Text) na folders da files,
    kuma yana lika title din kowane shafin HTML a matsayin bayani.
    """
    output = ""
    if not os.path.exists(current_dir):
        return output
        
    elements = os.listdir(current_dir)
    elements = [e for e in elements if e not in ["api_spec.json", "explorer.json", "explorer_visual.txt"]]
    
    for i, elem in enumerate(sorted(elements)):
        path = os.path.join(current_dir, elem)
        is_last = (i == len(elements) - 1)
        connector = "└── " if is_last else "├── "
        
        # Idan HTML file ne, mu nemo title dinsa domin sakawa a visual tree
        if os.path.isfile(path) and elem.endswith(".html"):
            page_title = get_html_title(path)
            output += f"{prefix}{connector}{elem}  📌 ({page_title})\n"
        else:
            output += f"{prefix}{connector}{elem}\n"
            
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            output += generate_visual_tree(base_path, path, new_prefix)
    return output

def generate_website_explorer(domain):
    """
    Babban inji mai hada Frontend Route Map da Hadaddun Virtual Backend API paths
    tare da sanya <title> na kowane shafi a cikin explorer.json.
    """
    base_folder = os.path.join("data", domain)
    api_spec_path = os.path.join(base_folder, "api_spec.json")
    output_json_path = os.path.join(base_folder, "explorer.json")
    output_txt_path = os.path.join(base_folder, "explorer_visual.txt")
    
    explorer_tree = {"domain": domain, "website_routes": []}
    if not os.path.exists(base_folder): 
        return

    # I. TSARRAFA FRONTEND ROUTES (HTML, JS, CSS)
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file in ["api_spec.json", "explorer.json", "explorer_visual.txt"]: 
                continue
                
            actual_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(actual_file_path, base_folder)
            ext = os.path.splitext(file)[1].lower()
            ftype = ext.lstrip('.') if ext else "unknown"
            
            # Tace tsaftar URL Route
            if file.endswith(".html"):
                if file == "index.html":
                    route_path = "/" if relative_path == "index.html" else f"/{os.path.dirname(relative_path)}/"
                else:
                    clean_name = os.path.splitext(file)[0]
                    dir_name = os.path.dirname(relative_path)
                    route_path = f"/{dir_name}/{clean_name}/" if dir_name and dir_name != "." else f"/{clean_name}/"
                actual_file = "index.html"
                # Ciro title na asali
                page_title = get_html_title(actual_file_path)
            else:
                route_path = f"/{relative_path.replace(os.sep, '/')}"
                actual_file = file
                page_title = None

            route_path = "/" + route_path.strip("/")
            if ext == ".html" and not route_path.endswith("/"): 
                route_path += "/"

            route_data = {
                "path": route_path,
                "file": actual_file,
                "type": "html" if ftype == "html" else ftype,
                "format": ext
            }
            
            # Idan shafin HTML ne, sanya kaddarar title a ciki
            if page_title is not None:
                route_data["title"] = page_title

            explorer_tree["website_routes"].append(route_data)

    # II. SHIGO DA TSAFTATATTUN BACKEND API ENDPOINTS
    api_routes_list = []
    if os.path.exists(api_spec_path):
        try:
            with open(api_spec_path, "r", encoding="utf-8") as f:
                api_data = json.load(f)
            for api_route in api_data.keys():
                api_routes_list.append(api_route)
                api_file = api_route.split("/")[-1]
                explorer_tree["website_routes"].append({
                    "path": api_route,
                    "file": api_file if api_file else "index.php",
                    "type": "json",
                    "format": os.path.splitext(api_file)[1].lower() or ".php"
                })
        except Exception: pass

    # Ajiye explorer.json
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(explorer_tree, f, indent=4, ensure_ascii=False)

    # III. GINA DYNAMIC EXPLORER_VISUAL.TXT
    visual_tree_text = f"📂 {domain} (Enterprise Frontend Map Layout)\n"
    visual_tree_text += generate_visual_tree(base_folder, base_folder)
    
    # Loda ingantaccen tsarin API filla-filla a kasa
    visual_tree_text += "\n⚙️ Simulated Backend API Endpoint Tree\n"
    if api_routes_list:
        for i, route in enumerate(sorted(list(set(api_routes_list)))):
            is_last = (i == len(api_routes_list) - 1)
            connector = "└── " if is_last else "├── "
            visual_tree_text += f"{connector}{route}\n"
    else:
        visual_tree_text += "└── [No API Endpoints Captured]\n"
        
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(visual_tree_text)
        
    print(f"   [🎯 TITLE-READY MAP COMPLETE] Directory mapped with exact metadata successfully!")
