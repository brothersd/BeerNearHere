from django.urls import path
from . import views

urlpatterns = [
    # Endpoint for the community reviews page
    path('all-reviews/', views.all_reviews, name='all-reviews'),
    
    # Endpoint for submitting a new review to a specific product
    path('<int:product_id>/reviews/', views.create_review, name='create-review'),
]