from django.urls import path
from .views import latest_kospi_data, top3_close_price

urlpatterns = [
    path('api/latest/', latest_kospi_data, name='latest_kospi_data'),
    path('api/top3-close-price', top3_close_price, name='top3_close_price'),
]