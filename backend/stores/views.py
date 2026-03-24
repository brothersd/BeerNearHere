# backend/stores/views.py
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from stores.models import StoreProduct
from stores.serializers import StoreSerializer
from stores.spiders.kroger import sync_kroger_products
from stores.spiders.walmart import search_products as walmart_search_products
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

PRODUCT_TTL_DAYS = 30
MAX_RESULTS_PER_STORE = 20


@api_view(['GET'])
@api_view(['HEAD'])
def health_check(request):
    """
    Health check endpoint for Docker/Kubernetes readiness probes.
    
    GET /health/ - Returns detailed health status with component checks
    HEAD /health/ - Returns only headers (for liveness probe)
    """
    # Check database connectivity
    db_healthy = False
    try:
        StoreProduct.objects.count()  # Simple query to test DB connection
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check application components
    components_status = {
        "api": "healthy",
        "database": "healthy" if db_healthy else "unhealthy",
        "walmart_api": "unknown",  # Requires credentials to test
        "kroger_api": "unknown",   # Requires credentials to test
    }
    
    # Try Walmart API health check (if credentials available)
    try:
        from stores.spiders.walmart import load_walmart_credentials
        CONSUMER_ID, PRIVATE_KEY_PATH, KEY_VERSION = load_walmart_credentials()
        components_status["walmart_api"] = "healthy"
    except ValueError as e:
        logger.warning(f"Walmart credentials not configured (expected in dev): {e}")
        components_status["walmart_api"] = "not_configured"
    except Exception as e:
        logger.error(f"Walmart API health check failed: {e}")
        components_status["walmart_api"] = "unhealthy"
    
    # Try Kroger API health check (if credentials available)
    try:
        from utils.OAuth2 import get_token
        token = get_token()
        if token:
            components_status["kroger_api"] = "healthy"
        else:
            logger.warning("Kroger token fetch failed")
            components_status["kroger_api"] = "unhealthy"
    except ValueError as e:
        logger.warning(f"Kroger credentials not configured (expected in dev): {e}")
        components_status["kroger_api"] = "not_configured"
    except Exception as e:
        logger.error(f"Kroger API health check failed: {e}")
        components_status["kroger_api"] = "unhealthy"
    
    overall_healthy = all(
        status == "healthy"
        for status in components_status.values()
        if status != "not_configured"
    )
    
    response_data = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", timezone.now().timetuple()),
        "components": components_status,
    }
    
    # HEAD request returns only headers
    if request.method == 'HEAD':
        return Response(status=status.HTTP_200_OK)
    
    return Response(response_data, status=status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def ready_check(request):
    """
    Readiness check - verifies application is ready to accept traffic.
    Used by Kubernetes liveness/readiness probes.
    """
    # Check database connectivity
    try:
        StoreProduct.objects.count()
    except Exception as e:
        logger.error(f"Database not available for readiness check: {e}")
        return Response(
            {"status": "not_ready", "reason": "database_unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # Check that we can perform a basic query with ordering (used in search)
    try:
        StoreProduct.objects.order_by('price').count()
    except Exception as e:
        logger.error(f"Database query failed for readiness check: {e}")
        return Response(
            {"status": "not_ready", "reason": "database_query_failed"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response({"status": "ready"})


@api_view(['GET'])
def live_check(request):
    """
    Liveness check - verifies application process is alive.
    Used by Kubernetes liveness probes (restart container if unhealthy).
    Always returns healthy unless there's a critical error.
    """
    return Response({"status": "alive"})


PACK_SIZE_KEYWORDS = {
    'single':   ['single', ' 1 ct', ' 1 can', ' 1 bottle', '16 oz', '40 oz', '12 oz', '24 fl oz', '25 fl oz'],
    '6 pack':   ['6 pack', '6-pack', '6pk', '6 pk', '6 ct', '6 cans', '6 can', '6 bottles', '6 bottle'],
    '12 pack':  ['12 pack', '12-pack', '12pk', '12 pk', '12 ct', '12 cans', '12 can', '12 bottles', '12 bottle'],
    '15 pack':  ['15 pack', '15-pack', '15pk', '15 pk', '15 ct', '15 cans', '15 can', '15 bottles', '15 bottle'],
    '18 pack':  ['18 pack', '18-pack', '18pk', '18 pk', '18 ct', '18 cans', '18 can', '18 bottles', '18 bottle'],
    '24 pack':  ['24 pack', '24-pack', '24pk', '24 pk', '24 ct', '24 cans', '24 can', '24 bottles', '24 bottle'],
    '30 pack':  ['30 pack', '30-pack', '30pk', '30 pk', '30 ct', '30 cans', '30 can', '30 bottles', '30 bottle'],
    '36 pack':  ['36 pack', '36-pack', '36pk', '36 pk', '36 ct', '36 cans', '36 can', '36 bottles', '36 bottle'],
}


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Beer Near Here API',
        'version': '1.0.0',
        'endpoints': {
            'search': '/api/search/ (POST)',
            'docs': '/api/docs/',
        }
    })


def sync_walmart_products(zip_code: str, product_name: str, search_term: str) -> int:
    data = walmart_search_products(query=search_term, limit=MAX_RESULTS_PER_STORE, zip_code=zip_code)
    if not data:
        return 0
    items = data.get('items', [])
    saved_count = 0
    for item in items:
        name = item.get('name', '')
        price = item.get('salePrice')
        item_id = item.get('itemId', '')
        product_url = f"https://www.walmart.com/ip/{item_id}" if item_id else ''
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
    return saved_count


def filter_by_pack_size(queryset, pack_size: str):
    if not pack_size or pack_size not in PACK_SIZE_KEYWORDS:
        return queryset
    from django.db.models import Q
    query = Q()
    for kw in PACK_SIZE_KEYWORDS[pack_size]:
        query |= Q(name__icontains=kw)
    return queryset.filter(query)


class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @api_view(['GET'])
    def get_health_status(self, request):
        """Return health status for this view."""
        return Response({
            "status": "healthy",
            "message": "Product search service is operational"
        })

    def get(self, request):
        return Response({
            'message': 'Send POST to /api/search/ with zip_code, product_name, and optional pack_size',
            'example': {'zip_code': '80918', 'product_name': 'beer', 'pack_size': '6 pack'}
        })

    def post(self, request):
        zip_code = request.data.get('zip_code')
        product_name = request.data.get('product_name')
        pack_size = request.data.get('pack_size', '').strip().lower()

        if not zip_code or not product_name:
            return Response(
                {"error": "Both zip_code and product_name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        search_term = f"{product_name} {pack_size}".strip() if pack_size else product_name

        try:
            cutoff = timezone.now() - timedelta(days=PRODUCT_TTL_DAYS)
            deleted_count, _ = StoreProduct.objects.filter(created_at__lt=cutoff).delete()
            if deleted_count:
                logger.info(f"Purged {deleted_count} products older than {PRODUCT_TTL_DAYS} days")

            kroger_count = sync_kroger_products(zip_code, product_name, limit=MAX_RESULTS_PER_STORE)
            logger.info(f"Kroger sync saved {kroger_count} products for '{product_name}' in {zip_code}")

            walmart_count = sync_walmart_products(zip_code, product_name, search_term)
            logger.info(f"Walmart sync saved {walmart_count} products for '{product_name}' in {zip_code}")

            products = StoreProduct.objects.filter(
                name__icontains=product_name,
                zip_code=zip_code
            )
            products = filter_by_pack_size(products, pack_size)
            products = products.order_by('price')

            serializer = StoreSerializer(products, many=True)

            return Response({
                "count": len(serializer.data),
                "pack_size": pack_size or None,
                "results": serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.warning(f"Invalid input for search: {e}")
            return Response(
                {"error": "Invalid request parameters. Please check your zip code and product name."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log full error for debugging, but send user-friendly message to client
            logger.error(f"Search failed: {type(e).__name__}: {str(e)}", exc_info=True)
            
            # Check if this is a database/connection issue (transient error)
            db_error_types = [
                'DatabaseError',
                'OperationalError',
                'ConnectionError',
                'Timeout'
            ]
            error_type_name = type(e).__name__
            
            if any(err in error_type_name for err in db_error_types):
                # Retry transient database errors with exponential backoff
                logger.info(f"Transient DB error, will retry: {error_type_name}")
                max_retries = 3
                base_delay = 1.0
                
                for attempt in range(max_retries):
                    try:
                        cutoff = timezone.now() - timedelta(days=PRODUCT_TTL_DAYS)
                        deleted_count, _ = StoreProduct.objects.filter(created_at__lt=cutoff).delete()
                        if deleted_count:
                            logger.info(f"Purged {deleted_count} products older than {PRODUCT_TTL_DAYS} days")
                        
                        kroger_count = sync_kroger_products(zip_code, product_name, limit=MAX_RESULTS_PER_STORE)
                        logger.info(f"Kroger sync saved {kroger_count} products for '{product_name}' in {zip_code}")
                        
                        walmart_count = sync_walmart_products(zip_code, product_name, search_term)
                        logger.info(f"Walmart sync saved {walmart_count} products for '{product_name}' in {zip_code}")
                        
                        products = StoreProduct.objects.filter(
                            name__icontains=product_name,
                            zip_code=zip_code
                        )
                        products = filter_by_pack_size(products, pack_size)
                        products = products.order_by('price')
                        
                        serializer = StoreSerializer(products, many=True)
                        
                        return Response({
                            "count": len(serializer.data),
                            "pack_size": pack_size or None,
                            "results": serializer.data
                        }, status=status.HTTP_200_OK)
                    except Exception as retry_error:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.info(f"Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                        else:
                            raise
                
            return Response(
                {"error": "An error occurred during the search. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = StoreProduct.objects.all().order_by('-created_at')
        serializer = StoreSerializer(products, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
