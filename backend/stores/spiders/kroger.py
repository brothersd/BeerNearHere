# /backend/stores/spiders/kroger.py
import logging
import requests
from utils.OAuth2 import get_token
from utils.config import search_radius
from stores.models import StoreProduct

logger = logging.getLogger(__name__)

# API Endpoints
LOCATIONS_URL = "https://api.kroger.com/v1/locations"
PRODUCTS_URL = "https://api.kroger.com/v1/products"


def _get_headers(banner: str = "kingsoopers") -> dict | None:
    """
    Fetches a fresh OAuth2 token and returns request headers.
    Returns None if token fetch fails.
    """
    access_token = get_token()
    if not access_token:
        logger.error("Failed to get Kroger access token.")
        return None
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "X-Kroger-Banner": banner
    }


def get_nearby_locations(zip_code: str, headers: dict, limit: int = 1, radius: int = search_radius) -> list:
    """Fetches the nearest store location(s) based on ZIP code."""
    
    params = {
        "filter.zipCode.near": zip_code,
        "filter.limit": limit,
        "filter.radius": radius
    }
    try:
        response = requests.get(LOCATIONS_URL, headers=headers, params=params, timeout=60)
        if response.status_code == 200:
            return response.json().get('data', [])
        logger.error(f"Location Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Location request failed: {e}")
    return []


def get_products_at_location(location_id: str, term: str, headers: dict, limit: int = 20) -> list:
    """Fetches products for a specific store location."""
    
    params = {
        "filter.term": term,
        "filter.locationId": location_id,
        "filter.limit": limit
    }
    try:
        response = requests.get(PRODUCTS_URL, headers=headers, params=params, timeout=60)
        if response.status_code == 200:
            return response.json().get('data', [])
        logger.error(f"Product Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Product request failed: {e}")
    return []


def sync_kroger_products(zip_code: str, product_name: str, banner: str = "kingsoopers", limit: int = 20) -> int:
    """
    Main entry point for views.py.
    Fetches products from the nearest Kroger banner store and saves them to the DB.
    Returns the count of products saved/updated.
    """
    logger.info(f"Starting Kroger sync: '{product_name}' near {zip_code} ({banner})")

    headers = _get_headers(banner)
    if not headers:
        return 0

    locations = get_nearby_locations(zip_code, headers=headers)
    if not locations:
        logger.warning(f"No {banner} locations found near {zip_code}")
        return 0

    location = locations[0]
    location_id = location.get('locationId')
    store_name = location.get('name', banner.capitalize())
    logger.info(f"Found store: {store_name} (ID: {location_id})")

    products = get_products_at_location(location_id, product_name, headers=headers, limit=limit)
    if not products:
        logger.warning(f"No products found for '{product_name}' at {store_name}")
        return 0

    saved_count = 0
    for prod in products:
        name = prod.get('description', '')
        product_id = prod.get('productId')
        items = prod.get('items', [])

        if not name or not product_id or not items:
            continue

        # Only process products that match the search term
        if product_name.lower() not in name.lower():
            continue

        price_info = items[0].get('price', {})
        regular = price_info.get('regular', 0)
        promo = price_info.get('promo', 0)
        final_price = promo if (promo and 0 < promo < regular) else regular

        if not final_price:
            continue

        # Append size info (e.g. "24 cans / 12 fl oz") to name so pack size filtering works
        size = items[0].get('size', '')
        display_name = f"{name} - {size}" if size else name

        from urllib.parse import quote
        slug = quote(name.lower().replace(' ', '-'), safe='-')
        #slug = name.lower().replace(' ', '-').replace('/', '-')
        product_url = f"https://www.kroger.com/p/{slug}/{product_id}"

        StoreProduct.objects.update_or_create(
            product_url=product_url,
            defaults={
                'name': display_name,
                'price': final_price,
                'store_name': store_name,
                'zip_code': zip_code,
            }
        )
        saved_count += 1
        logger.info(f"Saved: {display_name} @ ${final_price:.2f}")

    logger.info(f"Kroger sync complete: {saved_count} products saved/updated")
    return saved_count


# --- Standalone testing ---
if __name__ == "__main__":
    count = sync_kroger_products(zip_code="80918", product_name="milk", banner="kingsoopers")
    print(f"Done. {count} products saved.")