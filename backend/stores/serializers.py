from rest_framework import serializers
from .models import StoreProduct, Review


class ReviewSerializer(serializers.ModelSerializer):
    # Read-only fields for display in the UI
    username = serializers.ReadOnlyField(source='user.username')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Review
        fields = ['id', 'product', 'username', 'product_name', 'rating', 'content', 'created_at']
        # FIX: Added 'product' to read_only_fields so DRF doesn't expect it in the request payload.
        # The view handles attaching the product instance via serializer.save(product=product).
        read_only_fields = ['id', 'username', 'product_name', 'created_at', 'product']

    def validate_rating(self, value):
        """Ensure the rating is between 1 and 5 stars."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class StoreSerializer(serializers.ModelSerializer):
    # Nest reviews within the product data for search results
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = StoreProduct
        fields = ['id', 'name', 'price', 'store_name', 'zip_code', 'product_url', 'created_at', 'reviews']
        read_only_fields = ['id', 'created_at']