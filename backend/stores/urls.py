# backend/stores/urls.py
from django.urls import path
from . import views
from . import auth_views

app_name = 'stores'

urlpatterns = [
    # Root API endpoint (for testing)
    path('', views.api_root, name='api-root'),

    # Auth endpoints
    path('auth/register/', auth_views.RegisterView.as_view(), name='register'),
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/change-password/', auth_views.ChangePasswordView.as_view(), name='change-password'),
    path('auth/delete-account/', auth_views.DeleteAccountView.as_view(), name='delete-account'),

    # Product endpoints
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
]
