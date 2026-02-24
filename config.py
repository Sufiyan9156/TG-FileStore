import os

def get_env(name, default=None, cast=str):
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    try:
        return cast(value)
    except:
        raise RuntimeError(f"Invalid type for env variable: {name}")

API_ID = get_env("API_ID", cast=int)
API_HASH = get_env("API_HASH")
BOT_TOKEN = get_env("BOT_TOKEN")
DB_URI = get_env("DB_URI")
DB_NAME = get_env("DB_NAME")

ADMINS = list(map(int, get_env("ADMINS").split()))
WORKERS = int(get_env("WORKERS", 5))
