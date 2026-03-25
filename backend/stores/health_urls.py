# Health check URLs for Docker/Kubernetes probes
from django.urls import path, include
from .views import health_check, ready_check, live_check

app_name = 'health'

urlpatterns = [
    path('ready/', ready_check, name='readiness-check'),
    path('live/', live_check, name='liveness-check'),
]
