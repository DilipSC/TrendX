import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory containing utils.py
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env.local file with absolute path
load_dotenv(BASE_DIR / '.env.local', override=True)

# Twitter Credentials
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

# ProxyMesh Configuration
PROXY_URL = os.getenv("PROXY_URL")

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "twitter_trends")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "trends")

# Debug print statements
print("Environment variables loaded from:", str(BASE_DIR / '.env.local'))
print(f"TWITTER_USERNAME: {'set' if TWITTER_USERNAME else 'not set'}")
print(f"TWITTER_PASSWORD: {'set' if TWITTER_PASSWORD else 'not set'}")
print(f"MONGO_URI: {'set' if MONGO_URI else 'not set'}")
print(f"PROXY_URL: {'set' if PROXY_URL else 'not set'}")

# Validate required environment variables
if not TWITTER_USERNAME or not TWITTER_PASSWORD:
    raise ValueError(
        "Missing Twitter credentials. Please make sure TWITTER_USERNAME and "
        "TWITTER_PASSWORD are set in your .env.local file"
    )

if not MONGO_URI:
    raise ValueError(
        "Missing MongoDB URI. Please make sure MONGO_URI is set in your .env.local file"
    )
