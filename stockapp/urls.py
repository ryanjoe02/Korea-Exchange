from django.urls import path
from .views import latest_kospi_data, top3_close_price, CustomTokenCreateView

urlpatterns = [
    path('api/latest/', latest_kospi_data, name='latest_kospi_data'),
    path('api/top3-close-price/', top3_close_price, name='top3_close_price'),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='custom_token_create'),
]