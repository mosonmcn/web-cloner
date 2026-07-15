import requests
import json

def live_sniff_response(base_url, route, method, payload_keys):
    """
    Mataki na 3: Yana aika kiran gaske zuwa ga API endpoint 
    domin kwaso ainihin tsarin JSON Response (Structure).
    """
    # 1. Gina cikakken URL
    if not route.startswith("http"):
        if base_url.endswith("/") and route.startswith("/"):
            full_url = base_url + route[1:]
        elif not base_url.endswith("/") and not route.startswith("/"):
            full_url = base_url + "/" + route
        else:
            full_url = base_url + route
    else:
        full_url = route

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11) Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }

    # 2. Haɗa danyen Payload na jabu idan Method ɗin POST ne
    mock_payload = {}
    if method.upper() == "POST" and payload_keys:
        for key in payload_keys:
            # Sanya bayanan jabu dangane da sunan key ɗin don uwar garken kada ta yi fatali da request ɗin da wuri
            if "id" in key.lower() or "number" in key.lower() or "bvn" in key.lower() or "nin" in key.lower():
                mock_payload[key] = "1234567890"
            elif "amount" in key.lower() or "price" in key.lower() or "balance" in key.lower():
                mock_payload[key] = 1000
            else:
                mock_payload[key] = "test_data"

    try:
        # 3. Kaddamar da kiran intanet tare da Timeout na sakan 5
        if method.upper() == "POST":
            response = requests.post(full_url, json=mock_payload, headers=headers, timeout=5)
        else:
            response = requests.get(full_url, headers=headers, timeout=5)
            
        ctype = response.headers.get("Content-Type", "").lower()
        
        # 4. Idan abin da ya dawo JSON ne, mu ciro tsarin mu dawo da shi
        if "application/json" in ctype or "text/json" in ctype:
            try:
                json_data = response.json()
                # Idan JSON ɗin yana da tsawo sosai (kamar list na abubuwa), mu ɗauki samfurin farko kawai
                if isinstance(json_data, list) and len(json_data) > 0:
                    return json_data[0], ctype
                return json_data, ctype
            except Exception:
                return {"error": "Failed to parse returned JSON string"}, ctype
        else:
            # Idan ba JSON ba ne, mu adana irin danyen rubutun da ya dawo (misali HTML ko plain text)
            return {"raw_non_json_sample": response.text[:200]}, ctype

    except Exception as e:
        return {"connection_error": str(e)}, "failed"
