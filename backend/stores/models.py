# backend/stores/models.py
from django.db import models

class StoreProduct(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    store_name = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=5, default='')
    product_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
        verbose_name_plural = 'Store Products'
    
    def __str__(self):
        return f"{self.name} @ {self.store_name} (${self.price})"