from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    CalculatePriceView, 
    PricingConfigViewSet, 
    ConfigurationLogViewSet,
    APIRootView
)

router = DefaultRouter()
router.register(r'pricing-configs', PricingConfigViewSet)
router.register(r'configuration-logs', ConfigurationLogViewSet)

urlpatterns = [
    path('', APIRootView.as_view(), name='api_root'),
    path('calculate-price/', CalculatePriceView.as_view(), name='calculate_price'),
    path('', include(router.urls)),
] 