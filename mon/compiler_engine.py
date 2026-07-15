import re

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
        """
        Tsaftataccen Inji: Yana fitar da ainihin payload keys na gaske 
        ba tare da dauko sharar kalmomin HTML ko JS selectors ba.
        """
        payload_keys = set()
        if not self.scope_code: return []

        # A. Idan FormData ko URLSearchParams ne (Mafi aminci)
        append_matches = re.findall(r"\.(?:append|set)\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]", self.scope_code)
        for key in append_matches: 
            payload_keys.add(key)

        # B. Idan akwai URLSearchParams({key: val}) block
        search_params_matches = re.findall(r"URLSearchParams\(\s*\{{(.*?)\}}", self.scope_code, re.DOTALL)
        for block in search_params_matches:
            keys = re.findall(r"([a-zA-Z0-9_\-]+)\s*:", block)
            for key in keys: 
                if key.lower() not in ["html", "submit", "maxlength", "title"]:
                    payload_keys.add(key)

        # C. Idan JSON.stringify() ko danyen object aka jefa a matsayin body
        # Muna neman abubuwan da ke cikin { ... } na kusa da body ko kiran fetch
        json_blocks = re.findall(r"body\s*:\s*(?:JSON\.stringify\()?\{\s*(.*?)\s*\}", self.scope_code, re.DOTALL)
        if not json_blocks:
            # Idan an ayyana variable daban (e.g., const data = { ... })
            json_blocks = re.findall(r"(?:const|let|var)\s+[a-zA-Z0-9_]+\s*=\s*\{\s*(.*?)\s*\}", self.scope_code, re.DOTALL)
            
        for block in json_blocks:
            keys = re.findall(r"([a-zA-Z0-9_\-]+)\s*:", block)
            for key in keys:
                if key.lower() not in ["method", "headers", "body", "status", "mode", "credentials", "cache", "redirect", "html", "submit", "title"]:
                    payload_keys.add(key)

        return sorted(list(payload_keys))

    def extract_response_keys(self):
        response_keys = set()
        if not self.scope_code: return []
        
        # Ciro madaidaitan keys na response kamar data.success ko result.message
        resp_matches = re.findall(r'(?:result|data|res|response)\.([a-zA-Z0-9_\-]+)', self.scope_code)
        for key in resp_matches:
            if key not in ["json", "text", "xml", "ok", "status", "headers", "forEach", "length"]:
                response_keys.add(key)
        return sorted(list(response_keys))
