# main.py
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stores.spiders.kroger import sync_kroger_products
from stores.spiders.walmart import search_products, get_nearest_store_id
from stores.models import StoreProduct


def sync_walmart_products(zip_code: str, product_name: str) -> int:
    """
    Fetches products from Walmart and saves them to the DB.
    Returns the count of products saved/updated.
    """
    print(f"\n--- Checking Walmart for '{product_name}' near {zip_code} ---")
    data = search_products(query=product_name, limit=10, zip_code=zip_code)

    if not data:
        print("  No results from Walmart.")
        return 0

    items = data.get('items', [])
    saved_count = 0

    for item in items:
        name = item.get('name', '')
        price = item.get('salePrice')
        product_url = item.get('affiliateUrl', '')

        if not name or not price:
            continue

        if product_name.lower() not in name.lower():
            continue

        StoreProduct.objects.update_or_create(
            product_url=product_url,
            defaults={
                'name': name,
                'price': price,
                'store_name': 'Walmart',
                'zip_code': zip_code,
            }
        )
        saved_count += 1

    print(f"  Walmart: {saved_count} products saved/updated.")
    return saved_count


def display_results(zip_code: str, product_name: str):
    """Prints a combined price comparison table from the DB."""
    products = StoreProduct.objects.filter(
        name__icontains=product_name,
        zip_code=zip_code
    ).order_by('price')

    if not products:
        print("\n  No results found.")
        return

    print(f"\n{'='*60}")
    print(f"  Price comparison for '{product_name}' near {zip_code}")
    print(f"{'='*60}")
    print(f"  {'Store':<20} {'Price':<10} {'Product'}")
    print(f"  {'-'*55}")
    for p in products:
        price_str = f"${p.price:.2f}" if p.price else "N/A"
        print(f"  {p.store_name:<20} {price_str:<10} {p.name}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    zip_code = input("Enter Zip Code: ").strip()

    while True:
        search_term = input("\nWhat are you looking for? (or 'exit'): ").strip()
        if search_term.lower() == 'exit':
            break

        # Fetch from both stores
        print(f"\n--- Checking Kroger for '{search_term}' near {zip_code} ---")
        kroger_count = sync_kroger_products(zip_code, search_term)
        print(f"  Kroger: {kroger_count} products saved/updated.")

        walmart_count = sync_walmart_products(zip_code, search_term)

        # Display combined results
        display_results(zip_code, search_term)