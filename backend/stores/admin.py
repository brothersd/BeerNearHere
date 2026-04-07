from django.contrib import admin
from .models import StoreProduct

@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'store_name', 'updated_at')
    list_filter = ('store_name', 'created_at')
    search_fields = ('name', 'product_url')
    readonly_fields = ('created_at', 'updated_at')