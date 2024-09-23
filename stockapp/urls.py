from django.urls import path
from .views import (
    latest_kospi_data,
    top3_close_price,
    filter_kospi_data,
    CustomTokenCreateView,
    StockExportExcelAPIView,
    StockQueryAPIView,
)

urlpatterns = [
    path("api/latest/", latest_kospi_data, name="latest_kospi_data"),
    path("api/top3-close-price/", top3_close_price, name="top3_close_price"),
    path("api/filter-kospi", filter_kospi_data, name="filter_kospi_name"),
    path(
        "auth/token/login/", CustomTokenCreateView.as_view(), name="custom_token_create"
    ),
    path("api/stock-query/", StockQueryAPIView.as_view(), name="stock_query"),
    path("api/stock-export", StockExportExcelAPIView.as_view(), name="stock_export"),
]
