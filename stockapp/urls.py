from django.urls import path
from .views import get_stock_close

urlpatterns = [
    path('api/stock/<str:date>/', get_stock_close, name='get_stock_close'),
]