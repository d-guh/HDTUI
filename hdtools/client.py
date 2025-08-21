import os
import logging

import requests

BASE_URL = "https://hdtools.app.clemson.edu"

session = requests.Session()

def setup_session():
    """Sets the session headers, can be used for more in the future as needed"""
    session.headers.update({
        'Cookie': get_cookie(),
        'User-Agent': "HDToolsClient/1.0",
        'Accept': 'application/json'
    })

def get_cookie():
    """Gets the cookie from the envrionment variable or .env file"""
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

def test_cookie():
    """Validates the cookie by attempting to login to HDTools"""
    url = f"{BASE_URL}"
    try:
        logging.debug(f"GET {url}")
        r = session.get(url, allow_redirects=True)
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
    """Gets the available modules using the getModules.php endpoint"""
    url = f"{BASE_URL}/srv/util/getModules.php"
    logging.debug(f"GET {url}")
    r = session.get(url)
    logging.debug(f"Modules: {r.json()}")
    r.raise_for_status()
    return r.json()

def check_module_auth(module: str, vaultzid: str):
    """Checks if the current user is authenticated for a specific module. NOTE: Will likley not change much"""
    url = f"{BASE_URL}/srv/feed/dynamic/checkAuth/{module}/{vaultzid}"
    logging.debug(f"GET {url}")
    try:
        r = session.get(url)
        if r.status_code == 404:
            logging.debug(f"Module '{module}' not found (404). Skipping.")
            return None
        r.raise_for_status()
        return r.json() # Acts as bool, response is plaintext 'true'
    except requests.RequestException as e:
        logging.debug(f"Failed auth check for module '{module}': {e}")
        return None

def get_name_by_id(vaultzid: str):
    """Gets the full name (and username) by vautzid"""
    url = f"{BASE_URL}/srv/feed/dynamic/rest/NameByID/{vaultzid}"
    logging.debug(f"GET {url}")
    r = session.get(url)
    r.raise_for_status()
    return r.json()

def get_module(module: str, vaultzid: str):
    """Gets a specified module"""
    url = f"{BASE_URL}/srv/feed/dynamic/rest/{module}/{vaultzid}"
    logging.debug(f"GET {url}")
    r = session.get(url)
    r.raise_for_status()
    return r.json()

def get_vault_module(vaultzid: str):
    """Gets the vault module specifically since it has a different response format"""
    url = f"{BASE_URL}/srv/feed/dynamic/rest/eventLogNew/{vaultzid}?extended=1"
    logging.debug(f"GET {url}")
    r = session.get(url)
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
    """Formatter for vault history, uses list of objects, different response from other modules"""
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

def search_user(query: str):
    """Searches for a user by username or name (query)"""
    url = f"{BASE_URL}/srv/feed/dynamic/rest/Search/{query}"
    logging.debug(f"GET {url}")
    response = session.get(url)

    response.raise_for_status()
    logging.debug(f"Response status: {response.status_code}")
    # logging.debug(f"Response data: {response.json()}")
    return response.json()

def parse_username(username: str):
    """Removes whitespace and clemson email from username"""
    return username.strip().removesuffix('@clemson.edu').removesuffix('@g.clemson.edu')

# Similar to search, but more script friendly
def get_user_data(user: str):
    """Gets a users' data from search by username, script friendly"""
    username = parse_username(user)
    url = f"{BASE_URL}/srv/feed/dynamic/rest/Search/{username}"
    logging.debug(f"GET {url}")
    response = session.get(url)
    data = response.json()
    if isinstance(response, dict) and 'ErrorMessage' in data:
        error = data['ErrorMessage']
        raise Exception(f"Unable to get user {username}: {error}")
    elif not isinstance(data, list):
        raise Exception(f"Unable to get user {username}: unknown data returned")
    elif len(data) == 0:
        raise Exception(f"Unable to get user {username}: no users returned")

    return data[0]

def extract_id_and_username(user_json: dict) -> tuple[str, str]:
    """Extracts a users vaultzid and username from user's json"""
    vaultzid = user_json.get('zid', None)
    if vaultzid is None:
        raise Exception('Data does not contain Vaultzid!')

    primary_username = user_json.get('primaryUserName', [])
    if primary_username is None:
        raise Exception('Data does not contain primary username!')

    logging.debug(f"Extracted username {primary_username} and id {vaultzid}")
    return vaultzid, primary_username[0]

def get_last_password_change(user: str):
    """Gets the time a users password was last changed"""
    logging.debug(f"Getting last password change for user: {user}")
    data = get_user_data(user)
    vaultzid, username = extract_id_and_username(data)

    if username is None:
        raise Exception(f"Username {username} not in data")

    url = f"{BASE_URL}/srv/feed/dynamic/rest/usernamesHDStudent/{vaultzid}"
    response = session.get(url)
    data = response.json()

    data = next((u for u in data['items'] if u['data']['label'].lower() == username.lower()), None)

    reset_time = data['data']['passwordChangedTime']

    return reset_time

def get_user_status(user: str):
    """Gets the users current status (health-good = active)"""
    user_health = search_user(user)[0].get("userNamesHealth", None)
    status = user_health.get(user.lower(), None)
    return (status == "health-good")

def get_abroad_status(user: str):
    """Checks if the user is studying abroad (TSAP/SAP/CAP)"""
    zid, username = extract_id_and_username(search_user(user)[0])
    module = get_module('courses', zid)
    courses = module.get('items', [])[0].get('data', {})

    abroad_courses = {'TSAP', 'CAP', 'SAP'}

    for course in courses.keys():
        if isinstance(course, str) and any(tag in course.upper() for tag in abroad_courses):
            return True
    return False

def check_login(user: str, password: str):
    """Attempts to login using provided credentials"""
    session = requests.Session()
    session.get("https://logincheck.app.clemson.edu")
    r = session.post("https://idp.app.clemson.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1", data={"j_username" : user, "j_password" : password, "_eventId_proceed" : ''})

    return "duosecurity.com" in r.url
