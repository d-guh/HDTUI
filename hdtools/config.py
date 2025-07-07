import os

DEBUG = False

def debug(msg):
    if DEBUG:
        print(f"[DEBUG]: {msg}")

def load_dotenv(path=".env"):
    """Loads key=value pairs from .env, doesn't override content already present in environment variables"""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                if not os.environ.get(key):
                    os.environ[key] = val.strip()
