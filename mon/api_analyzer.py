import re
import os
import json
import posixpath

class JSCompilerCore:
    def __init__(self, js_code_content):
        self.js_code = js_code_content if js_code_content else ""

    def find_endpoint_locations(self, endpoint_keyword):
        locations = []
        if not self.js_code: return locations
        for match in re.finditer(re.escape(endpoint_keyword), self.js_code):
            locations.append(match.start())
        return locations

    def extract_function_scope(self, target_index):
        search_back = self.js_code[:target_index]
        open_bracket_index = search_back.rfind('{')
        if open_bracket_index == -1:
            line_start = search_back.rfind('\n') + 1
            line_end = self.js_code.find('\n', target_index)
            return self.js_code[line_start:line_end]

        bracket_count = 0
        function_end_index = -1
        for index in range(open_bracket_index, len(self.js_code)):
            char = self.js_code[index]
            if char == '{': bracket_count += 1
            elif char == '}': bracket_count -= 1
            
            if bracket_count == 0:
                function_end_index = index + 1
                break
        if function_end_index != -1:
            return self.js_code[open_bracket_index:function_end_index]
        return None

class JSAnalyzerBridge:
    def __init__(self, isolated_scope_content):
        self.scope_code = isolated_scope_content if isolated_scope_content else ""

    def extract_perfect_payload_keys(self):
        payload_keys = set()
        if not self.scope_code: return []

        # 1. Kwaso ainihin abubuwan .append() ko .set() na FormData
        append_matches = re.findall(r"\.(?:append|set)\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]", self.scope_code)
        for key in append_matches: 
            payload_keys.add(key)

        # 2. Idan danyen body parameters ne (e.g., body: "user="+u+"&pass="+p)
        body_string_match = re.search(r"body\s*:\s*['\"`]([^'\"`]+)['\"`]", self.scope_code)
        if body_string_match:
            raw_body = body_string_match.group(1)
            string_keys = re.findall(r"([a-zA-Z0-9_\-]+)=", raw_body)
            for key in string_keys:
                payload_keys.add(key)

        # 3. Gyararren Regex na JSON.stringify ko danyen object (An gyara uwar gungun dake lahani)
        json_blocks = re.findall(r"body\s*:\s*(?:JSON\.stringify)?\s*\{\s*(.*?)\s*\}", self.scope_code, re.DOTALL)
        if not json_blocks:
            json_blocks = re.findall(r"(?:const|let|var)\s+[a-zA-Z0-9_]+\s*=\s*\{\s*(.*?)\s*\}", self.scope_code, re.DOTALL)
            
        for block in json_blocks:
            keys = re.findall(r"([a-zA-Z0-9_\-]+)\s*:", block)
            for key in keys:
                if key.lower() not in ["method", "headers", "body", "status", "mode", "credentials", "cache", "redirect", "html", "submit", "title"]:
                    payload_keys.add(key)

        return sorted(list(payload_keys))

def resolve_url_path(current_file_route, base_api_url, endpoint_path):
    if endpoint_path.startswith("http://") or endpoint_path.startswith("https://"):
        from urllib.parse import urlparse
        return urlparse(endpoint_path).path

    current_dir = posixpath.dirname(current_file_route)

    if base_api_url and not base_api_url.startswith("http"):
        combined_base = posixpath.normpath(posixpath.join(current_dir, base_api_url))
    else:
        combined_base = current_dir if not base_api_url else "/api"

    final_path = posixpath.normpath(posixpath.join(combined_base, endpoint_path))
    final_path = final_path.split('?')[0]
    if not final_path.startswith("/"):
        final_path = "/" + final_path

    return final_path

def extract_exact_js_response_schema(js_content, endpoint_func_context):
    schema = {}
    exact_keys = re.findall(r'(?:result|data|response)\.([a-zA-Z0-9_]+)', js_content)
    exact_keys = list(set([k for k in exact_keys if k not in ["json", "ok", "status_code"]]))
    
    for key in exact_keys:
        if key in endpoint_func_context or any(key in line for line in js_content.split('\n') if "result" in line or "data" in line):
            if "user" in key.lower():
                schema[key] = {"id": "TYPE_NUMBER", "name": "TYPE_STRING", "email": "TYPE_STRING", "token": "TYPE_STRING"}
            elif "transaction" in key.lower():
                schema[key] = [{"id": "TYPE_NUMBER", "reference": "TYPE_STRING", "amount": "TYPE_NUMBER", "status": "TYPE_STRING"}]
            elif "price" in key.lower() or "plan" in key.lower():
                schema[key] = {}
            else:
                schema[key] = "TYPE_UNKNOWN_DETERMINED_BY_JS"
                
    if "status" not in schema and "status" in exact_keys: schema["status"] = "TYPE_STRING"
    if "message" not in schema and "message" in exact_keys: schema["message"] = "TYPE_STRING"
    return schema

def advanced_static_analysis(js_content, current_file_route="/js/mainapi.js"):
    api_spec = {}
    if not js_content: return api_spec
    
    base_url_match = re.search(r'const\s+API_BASE_URL\s*=\s*[\'"`]([^\'"`]+)[\'"`]', js_content)
    base_api_url = base_url_match.group(1) if base_url_match else "../api"
    
    payload_format = "Raw JSON (application/json)"
    if "URLSearchParams" in js_content or "application/x-www-form-urlencoded" in js_content:
        payload_format = "Parameters (application/x-www-form-urlencoded)"
    elif "FormData" in js_content:
        payload_format = "Multipart FormData (multipart/form-data)"
        
    compiler = JSCompilerCore(js_content)
    lines = js_content.split('\n')
    
    for line in lines:
        if "apiCall" in line or "fetch" in line:
            endpoint_match = re.search(r'(?:apiCall|fetch)\(\s*[\'"`]([^\'"`]+)[\'"`]', line)
            if endpoint_match:
                endpoint_path = endpoint_match.group(1)
                full_route = resolve_url_path(current_file_route, base_api_url, endpoint_path)
                
                func_name_match = re.search(r'(?:window\.)?([a-zA-Z0-9_]+)\s*=', line)
                if not func_name_match:
                    func_name_match = re.search(r'function\s+([a-zA-Z0-9_]+)', line)
                func_name = func_name_match.group(1) if func_name_match else "unknown_function"
                
                locations = compiler.find_endpoint_locations(endpoint_path)
                isolated_scope = ""
                if locations:
                    isolated_scope = compiler.extract_function_scope(locations[0])
                
                bridge = JSAnalyzerBridge(isolated_scope)
                payload_keys = bridge.extract_perfect_payload_keys()
                
                detected_keys = re.findall(r'(?:result|data|response)\.([a-zA-Z0-9_]+)', js_content)
                detected_keys = list(set([k for k in detected_keys if k not in ["json", "ok", "status_code"]]))
                
                exact_schema = extract_exact_js_response_schema(js_content, line)
                
                api_spec[full_route] = {
                    "function_purpose": func_name,
                    "method": "GET" if "GET" in line.upper() else "POST",
                    "expected_payload_format": payload_format,
                    "guessed_payload_keys": sorted(payload_keys), 
                    "js_response_reading_keys": detected_keys,
                    "extracted_response_schema_from_js": exact_schema,
                    "raw_js_context": line.strip()
                }
    return api_spec

def save_api_spec(domain, new_spec):
    folder = os.path.join("data", domain)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "api_spec.json")
    
    existing_spec = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: existing_spec = json.load(f)
        except Exception: pass
            
    existing_spec.update(new_spec)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_spec, f, indent=4, ensure_ascii=False)