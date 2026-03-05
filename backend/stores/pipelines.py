from asgiref.sync import sync_to_async
from stores.models import StoreProduct

class StoreProductPipeline:
    # Added 'spider' argument to fix the DeprecationWarning from your logs
    async def process_item(self, item, spider):
        await sync_to_async(self.save_or_update)(item)
        return item

    def save_or_update(self, item):
        # This performs the 'U' (Update) and 'C' (Create) of CRUD
        StoreProduct.objects.update_or_create(
            product_url=item.get('product_url'),
            defaults={
                'name': item.get('name'),
                'price': item.get('price'),
                'store_name': item.get('store_name'),
                'zip_code': item.get('zip_code', ''),
            }
        )