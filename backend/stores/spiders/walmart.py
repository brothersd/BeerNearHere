import os
import sys
import time
import json
import requests
import base64
import logging
import argparse
from pathlib import Path
from typing import cast, Optional
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- LOAD CREDENTIALS FROM ENV ---
CONSUMER_ID = os.getenv("WALMART_CONSUMER_ID")
PRIVATE_KEY_PATH = os.getenv("WALMART_PRIVATE_KEY_PATH", "./WM_IO_private_key.pem")
KEY_VERSION = os.getenv("WALMART_KEY_VERSION", "1")

# Validate credentials before proceeding
if not CONSUMER_ID:
    raise ValueError("❌ WALMART_CONSUMER_ID not found in .env file")
if not Path(PRIVATE_KEY_PATH).exists():
    raise FileNotFoundError(f"❌ Private key not found: {PRIVATE_KEY_PATH}")

logger.info("✅ Credentials loaded successfully")

# --- CACHE CONFIGURATION ---
CACHE_FILE = Path("./store_cache.json")
CACHE_TTL_SECONDS = 86400  # 24 hours


def generate_signature(consumer_id: str, timestamp: str, key_version: str, private_key_path: str) -> str:
    """Generate the RSA-SHA256 signature required by Walmart API."""
    string_to_sign = f"{consumer_id}\n{timestamp}\n{key_version}\n"
    
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    rsa_key = cast(RSAPrivateKey, private_key)

    signature_bytes = rsa_key.sign(
        string_to_sign.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature_bytes).decode('utf-8')


def load_store_cache() -> dict:
    """Load cached store lookups from disk."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
            return {}
    return {}


def save_store_cache(cache: dict):
    """Save store cache to disk."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save cache: {e}")


def get_store_id_by_zip(zip_code: str, max_stores: int = 1) -> list[dict]:
    """
    Lookup Walmart store IDs by zip code using the Affiliate Store Locator API.
    Returns list of stores with store number, name, distance, and address.
    """
    if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
        raise ValueError("Zip code must be a 5-digit string")
    
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(CONSUMER_ID, timestamp, KEY_VERSION, PRIVATE_KEY_PATH)
    
    headers = {
        "WM_CONSUMER.ID": CONSUMER_ID,
        "WM_SEC.AUTH_SIGNATURE": signature,
        "WM_SEC.KEY_VERSION": KEY_VERSION,
        "WM_CONSUMER.INTIMESTAMP": timestamp,
        "Accept": "application/json"
    }
    
    url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/stores"
    params = {"zip": zip_code, "limit": max_stores}
    
    try:
        logger.info(f"Looking up stores for zip {zip_code}...")
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # API returns a list directly, not a dict with a 'stores' key
        store_list = data if isinstance(data, list) else data.get('stores', [])

        stores = []
        for store in store_list:
            stores.append({
                'store_id': store.get('no'),
                'name': store.get('name'),
                'distance': store.get('distance'),
                'address': f"{store.get('streetAddress')}, {store.get('city')}, {store.get('stateProvCode')} {store.get('zip')}",
                'phone': store.get('phoneNumber')
            })
        return stores
    except requests.exceptions.HTTPError as e:
        logger.error(f"Store lookup HTTP Error: {e} - Response: {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Store lookup failed: {e}")
        return []


def get_nearest_store_id(zip_code: str) -> Optional[str]:
    """
    Get the nearest Walmart store ID for a zip code, with caching.
    Returns store 'no' (the ID used in product API calls) or None if not found.
    """
    cache = load_store_cache()
    
    if zip_code in cache:
        entry = cache[zip_code]
        if time.time() - entry['timestamp'] < CACHE_TTL_SECONDS:
            logger.info(f"Using cached store ID for {zip_code}")
            return entry['store_id']
        else:
            logger.info(f"Cache expired for {zip_code}, refreshing...")
    
    stores = get_store_id_by_zip(zip_code, max_stores=1)
    if stores:
        store_id = stores[0]['store_id']
        cache[zip_code] = {
            'store_id': store_id,
            'timestamp': time.time(),
            'store_name': stores[0]['name']
        }
        save_store_cache(cache)
        logger.info(f"Found store ID {store_id} for zip {zip_code} ({stores[0]['name']})")
        return store_id
    
    logger.warning(f"No stores found for zip {zip_code}")
    return None


def search_products(query: str, limit: int = 5, zip_code: Optional[str] = None) -> Optional[dict]:
    """
    Search Walmart products with optional location-based pricing via zip code.
    Returns API response data or None on failure.
    """
    store_id = None
    if zip_code:
        store_id = get_nearest_store_id(zip_code)
    
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(CONSUMER_ID, timestamp, KEY_VERSION, PRIVATE_KEY_PATH)
    
    headers = {
        "WM_CONSUMER.ID": CONSUMER_ID,
        "WM_SEC.AUTH_SIGNATURE": signature,
        "WM_SEC.KEY_VERSION": KEY_VERSION,
        "WM_CONSUMER.INTIMESTAMP": timestamp,
        "Accept": "application/json"
    }
    
    url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search"
    params = {"query": query, "limit": limit}
    if store_id:
        params["storeId"] = store_id
        logger.info(f"Searching with storeId={store_id} for location-aware results")
    
    try:
        logger.info(f"Sending request to Walmart API for query: '{query}'...")
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Log the keys of the first item to confirm available fields
        items = data.get('items', [])
        if items:
            logger.info(f"Walmart item keys: {list(items[0].keys())}")

        return data
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(f"Response: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def display_results(data: dict, max_items: int = 5):
    """Pretty-print search results."""
    print(f"\n✅ Success! Found {data.get('numberOfItems', 0)} items\n")
    
    items = data.get('items', [])[:max_items]
    if not items:
        print("  No items found.")
        return
    
    for i, item in enumerate(items, 1):
        name = item.get('name', 'N/A')
        price = item.get('salePrice', 'N/A')
        url = item.get('affiliateUrl', 'N/A')
        print(f"  {i}. {name}")
        print(f"     Price: ${price}")
        print(f"     URL: {url}")
        if 'storeId' in data.get('itemResponse', {}) or 'availableStores' in item:
            available = item.get('availableToSellQuantity', 'N/A')
            print(f"     Available: {available}")
        print()


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Walmart Product Search with Location Support")
    parser.add_argument("-q", "--query", type=str, default="laptop", help="Search query (default: laptop)")
    parser.add_argument("-l", "--limit", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("-z", "--zip", type=str, help="5-digit zip code for location-based pricing")
    parser.add_argument("--test-store", type=str, help="Test store lookup for a zip code and exit")
    return parser.parse_args()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    args = parse_arguments()
    
    if args.test_store:
        zip_code = args.test_store
        if len(zip_code) != 5 or not zip_code.isdigit():
            print("❌ Zip code must be 5 digits")
            sys.exit(1)
        
        stores = get_store_id_by_zip(zip_code, max_stores=3)
        if stores:
            print(f"\n📍 Stores near {zip_code}:")
            for s in stores:
                print(f"  • ID: {s['store_id']} | {s['name']}")
                print(f"    {s['address']} | {s['distance']} mi | 📞 {s['phone']}")
                print()
        else:
            print(f"❌ No stores found for {zip_code}")
        sys.exit(0)
    
    zip_code = args.zip or os.getenv("USER_ZIP_CODE")
    data = search_products(query=args.query, limit=args.limit, zip_code=zip_code)
    
    if data:
        display_results(data)
    else:
        print("\n❌ Failed to retrieve results. Check logs for details.")
        sys.exit(1)