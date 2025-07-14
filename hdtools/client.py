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
    r = requests.get(url, headers=get_headers())
    r.raise_for_status()
    return r.json()

def get_identity(vaultzid):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/identityHDStudent/Vaultzid={vaultzid},ou=Identities,o=cuvault"
    r = requests.get(url, headers=get_headers())
    r.raise_for_status()
    return r.json()

def format_identity(identity_json):
    try:
        item = identity_json["items"][0]
        data = item["data"]
        fields = item["properties"]["fields"]

        lines = []
        for field in fields:
            key = field.get("id")
            label = field.get("label", key)
            value = data.get(key, "")
            if value:
                lines.append(f"{label}: {value}")
        return "\n".join(lines)
    except Exception as e:
        return f"Failed to format identity: {e}"

def search_user(query):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/Search/{query}"
    logging.debug(f"GET {url}")
    response = requests.get(url, headers=get_headers())

    response.raise_for_status()
    logging.debug(f"Response status: {response.status_code}")
    # logging.debug(f"Response data: {response.json()}")
    return response.json()
