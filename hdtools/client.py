import os
import requests
import logging

BASE_URL = "https://hdtools.app.clemson.edu"

def get_cookie_header():
    if "HDTOOLS_COOKIE" in os.environ:
        cookie = os.environ["HDTOOLS_COOKIE"]
        logging.debug(f"Using full cookie: {cookie}")
        return cookie
    elif "HDTOOLS_COOKIE_NAME" in os.environ and "HDTOOLS_COOKIE_VALUE" in os.environ:
        name = os.environ["HDTOOLS_COOKIE_NAME"]
        value = os.environ["HDTOOLS_COOKIE_VALUE"]
        cookie = f"{name}={value}"
        logging.debug(f"Using split cookie: {cookie}")
        return cookie
    else:
        raise RuntimeError("Missing HDTools cookie in environment or .env")

def get_headers():
    headers = {
        'Cookie': get_cookie_header(),
        'User-Agent': "HDToolsClient/1.0",
        'Accept': 'application/json'
    }
    logging.debug(f"Request headers: {headers}")
    return headers

def test_cookie():
    url = f"{BASE_URL}"
    try:
        logging.debug(f"GET {url}")
        r = requests.get(url, headers=get_headers(), allow_redirects=True)
        final_url = r.url.lower()
        if "idp.app.clemson.edu" in final_url or "shib" in final_url:
            logging.debug(f"Redirected to {final_url}, cookie appears invalid.")
            return False
        return True
    except RuntimeError as e:
        logging.debug(f"Cookie test failed: {e}")
        return False
    except Exception as e:
        logging.debug(f"Unexpected error during cookie test: {e}")
        return False

def get_modules():
    url = f"{BASE_URL}/srv/util/getModules.php"
    logging.debug(f"GET {url}")
    r = requests.get(url, headers=get_headers())
    logging.debug(f"Modules: {r.json()}")
    r.raise_for_status()
    return r.json()

def check_module_auth(module, vaultzid):
    url = f"{BASE_URL}/srv/feed/dynamic/checkAuth/{module}/Vaultzid={vaultzid},ou=Identities,o=cuvault"
    logging.debug(f"GET {url}")
    try:
        r = requests.get(url, headers=get_headers())
        if r.status_code == 404:
            logging.debug(f"Module '{module}' not found (404). Skipping.")
            return None
        r.raise_for_status()
        return r.json() # Acts as bool, response is plaintext 'true'
    except requests.RequestException as e:
        logging.debug(f"Failed auth check for module '{module}': {e}")
        return None

def get_name_by_id(vaultzid):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/NameByID/Vaultzid={vaultzid},ou=Identities,o=cuvault"
    logging.debug(f"GET {url}")
    r = requests.get(url, headers=get_headers())
    r.raise_for_status()
    return r.json()

def get_module(module, vaultzid):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/{module}/Vaultzid={vaultzid},ou=Identities,o=cuvault"
    logging.debug(f"GET {url}")
    r = requests.get(url, headers=get_headers())
    r.raise_for_status()
    return r.json()

def get_vault_module(vaultzid):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/eventLogNew/Vaultzid={vaultzid},ou=Identities,o=cuvault?extended=1"
    logging.debug(f"GET {url}")
    r = requests.get(url, headers=get_headers())
    r.raise_for_status()
    return r.json()

def format_module(module_json):
    """Default formatter for modules, uses items and properties to display."""
    try:
        items = module_json.get("items", [])
        if not items:
            return "No data found."

        lines = []
        for item in items:
            data = item.get("data", {})
            fields = item.get("properties", {}).get("fields", [])
            for field in fields:
                key = field.get("id")
                label = field.get("label", key)
                value = data.get(key, "")
                if value:
                    lines.append(f"{label}: {value}")
        return "\n".join(lines)
    except Exception as e:
        return f"Failed to format module: {e}"

def format_vault_history(data):
    """Formatter for vault history, uses list of objects"""
    try:
        if not data:
            return "No vault history found."
    
        lines = []
        for entry in data[:10]:
            time = entry.get("datetime", "N/A")
            op = entry.get("operation", "N/A")
            name = entry.get("name", "N/A")
            reason = entry.get("reason", "N/A")

            lines.append(f"[{time}] {op} {name}")
            lines.append(f"  Reason: {reason}")
            lines.append("-" * 20)

        return "\n".join(lines)
    except Exception as e:
        return f"Failed to format vault history: {e}"

def search_user(query):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/Search/{query}"
    logging.debug(f"GET {url}")
    response = requests.get(url, headers=get_headers())

    response.raise_for_status()
    logging.debug(f"Response status: {response.status_code}")
    # logging.debug(f"Response data: {response.json()}")
    return response.json()
