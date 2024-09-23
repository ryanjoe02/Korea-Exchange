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

from .models import KospiData
from .serializers import (
    KospiDataSerializer,
    CustomTokenCreateSerializer,
    StockQuerySerializer,
)

# extract stock name and price using NLP
nlp = spacy.load("en_core_web_sm")


# connected CustomTokenCreateSerializer
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


# convert symbol to ticker
def search_ticker(company_name):
    url = "https://api.polygon.io/v3/reference/tickers"
    api_key = "dzXnuAc44Mz0POrWoppV7GxXqIeukDtU"

    params = {"search": company_name, "active": "true", "apiKey": api_key}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            ticker_symbol = data["results"][0]["ticker"]  # get a first ticker
            return ticker_symbol
        else:
            print(f"No ticker found for {company_name}")
            return None
    except Exception as e:
        print(f"Error fetching ticker for {company_name}: {e}")
        return None


def extract_stock_info(query):
    doc = nlp(query)

    stock_name = None
    price_threshold = None

    print(f"Entities in the query: {[ (ent.text, ent.label_) for ent in doc.ents ]}")

    # extract price and stock name
    for ent in doc.ents:
        if ent.label_ == "MONEY" or ent.label_ == "CARDINAL":
            price_threshold = ent.text
        elif (
            ent.label_ == "ORG" or ent.label_ == "GPE"
        ):  # organizations such as Apple, Samsung etc
            stock_name = ent.text

    # fall back to check for any proper nouns
    if stock_name:
        print(f"Searching ticker for: {stock_name}")
        stock_symbol = search_ticker(stock_name)

    print(f"Extracted stock_symbol : {stock_symbol}")
    print(f"Extracted price_threshold : {price_threshold}")

    return stock_symbol, price_threshold


# fetch stock data using yfinance
def get_stock_data(symbol):
    print(f"Fetching data for stock symbol: {symbol}")
    stock = yf.Ticker(symbol)
    hist = stock.history(peroid="1y")
    print(f"Fetched stock data: {hist.head()}")
    return hist


# view to process stock queries
class StockQueryAPIView(APIView):
    def post(self, request):
        serializer = StockQuerySerializer(data=request.data)

        if serializer.is_valid():
            query = serializer.validated_data.get("query")

            # extract stock symbol and price
            stock_symbol, price = extract_stock_info(query)

            if not stock_symbol or not price:
                return Response(
                    {"error": "Unable to extract stock information"}, status=400
                )

            try:
                # fetch stock data using yfinance
                data = get_stock_data(stock_symbol)

                # ensure data was returned
                if data.empty:
                    return Response(
                        {"error": "No stock data available for the given query"},
                        status=404,
                    )

                # filter for dates
                try:
                    price_float = float(price.replace(",", ""))
                    result = data[data["Close"] > price_float]
                except:
                    return Response({"error": "Invalid price value"}, status=400)

                if result.empty:
                    return Response(
                        {
                            "error": f"No dates found where {stock_symbol} exceeded {price}"
                        },
                        status=404,
                    )

                # return the last 3 results
                result = result.tail(3)
                response_data = result.reset_index()[["Date", "Close"]].to_dict(
                    orient="records"
                )

                return Response({"stock": stock_symbol, "result": response_data})

            except Exception as e:
                return Response({"error": str(e)}, status=500)

        return Response(serializer.errors, status=400)


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
