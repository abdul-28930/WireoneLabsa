from django.urls import path
from .api import CalculatePriceView

urlpatterns = [
    path('calculate-price/', CalculatePriceView.as_view(), name='calculate_price'),
] 