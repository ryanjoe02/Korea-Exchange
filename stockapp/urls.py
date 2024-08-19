from django.urls import path
from .views import latest_kospi_data

urlpatterns = [
    path('api/latest/', latest_kospi_data, name='latest_kospi_data'),
]