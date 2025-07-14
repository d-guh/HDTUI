import os
import logging

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
                if not os.environ.get(key) and val != '':
                    os.environ[key] = val.strip()

def init_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=level
    )
