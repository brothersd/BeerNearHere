# backend/stores/serializers.py
from rest_framework import serializers
from .models import StoreProduct

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = ['id', 'name', 'price', 'store_name', 'zip_code', 'product_url', 'created_at']
        read_only_fields = ['id', 'created_at']