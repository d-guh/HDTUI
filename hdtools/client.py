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

def search_user(username):
    url = f"{BASE_URL}/srv/feed/dynamic/rest/Search/{username}"
    logging.debug(f"GET {url}")
    response = requests.get(url, headers=get_headers())

    try:
        response.raise_for_status()
        logging.debug(f"Response status: {response.status_code}")
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON from server response.")
        print("Response body:")
        print(response.text[:500])
        raise
    except response.exceptions.HTTPError:
        print(f"HTTP Error {response.status_code}: {response.reason}")
        print("Response Body:")
        print(response.text[:500])
        raise
