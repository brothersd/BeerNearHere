import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from stores.models import StoreProduct, Review
from stores.serializers import StoreSerializer, ReviewSerializer
from stores.spiders.kroger import sync_kroger_products
from stores.spiders.walmart import search_products as walmart_search_products

logger = logging.getLogger(__name__)

PRODUCT_TTL_DAYS = 30
MAX_RESULTS_PER_STORE = 20

@api_view(['GET'])
@permission_classes([AllowAny])
def all_reviews(request):
    """
    Fetches all reviews with optimized user data joining.
    """
    reviews = Review.objects.select_related('user', 'product').all().order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy", "timestamp": timezone.now()}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def ready_check(request):
    try:
        StoreProduct.objects.exists()
        return Response({"status": "ready"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return Response({"status": "not ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
@permission_classes([AllowAny])
def live_check(request):
    return Response({"status": "alive"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "message": "Beer Near Here API is running",
        "endpoints": {
            "search": "/api/search/",
            "reviews": "/api/all-reviews/"
        }
    })

class ProductSearchView(APIView):
    """
    Handles search requests via POST (from client.js) or GET.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.handle_search(request)

    def get(self, request):
        return self.handle_search(request)

    def handle_search(self, request):
        # Extract data from POST body or GET query params
        data = request.data if request.method == 'POST' else request.query_params
        
        zip_code = data.get('zip_code', '').strip()
        product_name = data.get('product_name', '').strip()

        if not zip_code or not product_name:
            return Response(
                {"error": "Zip code and product name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove stale cached data
        stale_threshold = timezone.now() - timedelta(days=PRODUCT_TTL_DAYS)
        StoreProduct.objects.filter(updated_at__lt=stale_threshold).delete()

        try:
            # Trigger external scraping
            sync_kroger_products(zip_code, product_name)
            walmart_search_products(zip_code, product_name)

            # Query results back from local DB
            products = StoreProduct.objects.filter(
                name__icontains=product_name,
                zip_code=zip_code
            ).order_by('price')[:MAX_RESULTS_PER_STORE]
            
            serializer = StoreSerializer(products, many=True)
            return Response({
                "count": len(serializer.data),
                "results": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return Response({"error": "Search failed. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        products = StoreProduct.objects.all().order_by('-created_at')
        serializer = StoreSerializer(products, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id):
        try:
            product = StoreProduct.objects.get(id=product_id)
        except StoreProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id):
        reviews = Review.objects.select_related('user').filter(product_id=product_id).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewDeleteView(APIView):
    """
    Allows a user to delete ONLY their own review.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # 🔒 Security Check: Verify ownership
        if review.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this review."},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)
            
        if review.user != request.user:
            return Response({"error": "You can only delete your own reviews."}, status=403)
            
        review.delete()
        return Response(status=204)