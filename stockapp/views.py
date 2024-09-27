from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import HttpResponse

from datetime import datetime, timedelta
from io import BytesIO
import yfinance as yf
import pandas as pd
import spacy
import requests
import os
import time

from .models import KospiData
from .serializers import (
    KospiDataSerializer,
    CustomTokenCreateSerializer,
    StockQuerySerializer,
    StockDataSearchSerializer,
)

# extract stock name and price using NLP
nlp = spacy.load("en_core_web_sm")


##### CustomTokenCreateSerializer #####
class CustomTokenCreateView(APIView):
    permission_classes = [
        AllowAny
    ]  # This is because the token must be sent without authentication

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenCreateSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


##### stored kospi data in SQL (from 1996.12.11) #####
@api_view(["GET"])
def latest_kospi_data(request):
    fifty_days = datetime.now().date() - timedelta(days=10)
    latest_data = KospiData.objects.filter(date__gte=fifty_days).order_by("-date")
    serializer = KospiDataSerializer(latest_data, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def top3_close_price(request):
    top3_close_record = KospiData.objects.order_by("-close_price")[:3]

    if top3_close_record:
        response_data = [
            {
                "date": record.date,
                "close_price": record.close_price,
            }
            for record in top3_close_record
        ]
    else:
        response_data = {"error": "No data available"}

    return Response(response_data)


@api_view(["GET"])
def filter_kospi_data(request):
    close_price = request.query_params.get("close_price", None)

    if close_price is not None:
        kospi_data = KospiData.objects.filter(close_price__gt=close_price)
        serializer = KospiDataSerializer(kospi_data, many=True)

        return Response(serializer.data)

    return Response({"error": "No Close price provided."})


##### reqeust information from API #####
def extract_stock_info(query):
    doc = nlp(query)
    stock_name = None
    price_threshold = None
    comparison_type = "equal"  # default value

    # extract price and stock name
    for ent in doc.ents:
        if ent.label_ in ["MONEY", "CARDINAL"]:  # price
            price_threshold = ent.text
        elif ent.label_ in ["ORG", "GPE"]:  # company name
            stock_name = ent.text

    if "exceed" in query.lower() or "greater than" in query.lower():
        comparison_type = "greater_than_equal"
    elif "less than" in query.lower():
        comparison_type = "less_than_equal"
    elif "equal to" in query.lower():
        comparison_type = "equal"

    return stock_name, price_threshold, comparison_type


# view to process stock queries
def search_polygon_ticker(company_name):
    api_key = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/v3/reference/tickers?search={company_name}&active=true&apiKey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # extract relevant company
        company_options = [
            {
                "name": item.get("name", "N/A"),
                "ticker": item.get("ticker", "N/A"),
                "exchange": item.get("primary_exchange", "N/A"),
            }
            for item in data.get("results", [])
        ]

        return company_options
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching ticker for {company_name}: {e}")
        return []


class StockQueryAPIView(APIView):
    def post(self, request):
        serializer = StockQuerySerializer(data=request.data)

        if serializer.is_valid():
            query = serializer.validated_data.get("query")

            # 1. extract company name and price
            company, price, comparison_type = extract_stock_info(query)

            if not company or not price:
                return Response(
                    {"error": "Unable to extract stock information"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2. search for tickers
            company_options = search_polygon_ticker(company)

            print(company_options)

            if len(company_options) == 0:
                return Response(
                    {"error": "No stock data available for the given query"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 3. Return company and ticker
            return Response(
                {
                    "company_options": company_options,
                    "price": price,
                    "comparison_type": comparison_type,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##### search #####


# fetch stock data using yfinance
def get_stock_data(ticker, price, comparison_type):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    if hist.empty:
        return []

    if comparison_type == "greater_than_equal":
        result = hist[hist["Close"] >= float(price)]
    elif comparison_type == "less_than_equal":
        result = hist[hist["Close"] <= float(price)]

    return result.tail(5).reset_index()[["Date", "Close"]].to_dict(orient="records")


class StockDataSearchAPIView(APIView):
    def post(self, request):
        serializer = StockDataSearchSerializer(data=request.data)

        if serializer.is_valid():
            ticker = serializer.validated_data.get("ticker")
            price = serializer.validated_data.get("price")
            comparison_type = serializer.validated_data.get("comparison_type")

            # 4. fetch stock data and return
            stock_data = get_stock_data(ticker, price, comparison_type)

            if len(stock_data) == 0:
                return Response(
                    {"Error": "No stock data found for the given query"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Response data, latest 5 days
            return Response(
                {
                    "ticker": ticker,
                    "price": price,
                    "comparsion_type": comparison_type,
                    "stock_data": stock_data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# view to export data to Excel
class StockExportExcelAPIView(APIView):
    def post(self, request):
        serializer = StockQuerySerializer(data=request.data)

        if serializer.is_valid():
            query = serializer.validated_data.get("query")

            # extract stock info
            stock_symbol, price = extract_stock_info(query)

            if not stock_symbol or not price:
                return Response(
                    {"error": "Unable to extract stock information"}, status=400
                )

            # fetch stock data using yfinance
            try:
                data = get_stock_data(stock_symbol)
            except:
                return Response({"error": "Faild to retrieve stock data"}, status=404)

            # filter for dates where closing price exceeds the given price
            result = data[data["Close"] > float(price)]

            # convert result to pandas DataFrame
            df = result.reset_index()[["Date", "Close"]]

            # create excel file
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="openpyxl")
            df.to_excel(writer, index=False)
            writer.save()
            output.seek(0)

            response = HttpResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                f"attachment; filename={stock_symbol}_stock_data.xlsx"
            )
            return response

        return Response(serializer.errors, status=400)
