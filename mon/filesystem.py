import os
from urllib.parse import urlparse

def path_to_local(domain, path, content_type="text/html"):
    """
    Fasaha mai gyara kura-kuran sunayen fayiloli ta atomatik.
    Muna amfani da 'domain' mai dauke da lamba (_2) idan tsohuwa tana nan.
    """
    clean_path = path.split('?')[0]
    
    if clean_path == "/" or not clean_path.strip("/"):
        return os.path.join("data", domain, "index.html")
        
    parts = [p for p in clean_path.split('/') if p]
    last_part = parts[-1] if parts else ""
    has_extension = "." in last_part
    
    # AUTO-INDEX LOGIC
    if "text/html" in content_type.lower() and not has_extension:
        local_file_path = os.path.join("data", domain, *parts, "index.html")
    else:
        if "javascript" in content_type.lower() and not clean_path.endswith(".js"):
            clean_path += ".js"
        elif "css" in content_type.lower() and not clean_path.endswith(".css"):
            clean_path += ".css"
            
        local_file_path = os.path.join("data", domain, clean_path.lstrip("/"))

    dir_name = os.path.dirname(local_file_path)
    base_name = os.path.basename(local_file_path)
    
    if base_name == ".html":
        local_file_path = os.path.join(dir_name, "index.html")
        
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    
    return local_file_path
