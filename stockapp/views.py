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

from .models import KospiData
from .serializers import KospiDataSerializer,CustomTokenCreateSerializer,StockQuerySerializer

#connected CustomTokenCreateSerializer
class CustomTokenCreateView(APIView):
    permission_classes = [AllowAny] # This is because the token must be sent without authentication

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenCreateSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_OK)

@api_view(['GET'])
def latest_kospi_data(request):
    fifty_days = datetime.now().date() - timedelta(days=10)
    latest_data = KospiData.objects.filter(date__gte=fifty_days).order_by('-date')
    serializer = KospiDataSerializer(latest_data, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def top3_close_price(request):
    top3_close_record = KospiData.objects.order_by('-close_price')[:3]

    if top3_close_record:
        response_data = [
            {
                'date': record.date,
                'close_price' : record.close_price,
            }
            for record in top3_close_record
        ]
    else:
        response_data = {'error': 'No data available'}
    
    return Response(response_data)

@api_view(['GET'])
def filter_kospi_data(request):
    close_price = request.query_params.get('close_price', None)

    if close_price is not None:
        kospi_data = KospiData.objects.filter(close_price__gt=close_price)
        serializer = KospiDataSerializer(kospi_data, many=True)

        return Response(serializer.data)

    return Response({"error": "No Close price provided."})

# fetch stock data using yfinance
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(peroid="1y")
    return hist

# extract stock name and price
def extract_stock_info(query):
    words = query.split()
    stock_symbol = None
    price_threshold = None

    for word in words:
        if word.isdigit():
            price_threshold = word
        elif word.isalpha():
            stock_symbol = word
    
    return stock_symbol, price_threshold

# view to process stock queries
class StockQueryAPIView(APIView):
    def post(self, request):
        serializer = StockQuerySerializer(data=request.data)

        if serializer.is_valid():
            query = serializer.validated_data.get("query")

            # extract stock symbol and price
            stock_symbol, price = extract_stock_info(query)

            if not stock_symbol or not price:
                return Response({"error": "Unable to extract stock information"}, status=400)
            
            # fetch stock data using yfinance
            try:
                data = get_stock_data(stock_symbol)
            except:
                return Response({"error": "Faild to retrieve stock data"}, status=404)

            # filter for datas where closing price exceeded the given price
            result = data[data['Close'] > float(price)]
            # return the last 3 results
            result = result.tail(3)

            response_data = result.reset_index()[['Date', 'Close']].to_dict(orient='records')

            return Response({"stock": stock_symbol, "result": response_data})
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
                return Response({"error": "Unable to extract stock information"}, status=400)
            
            # fetch stock data using yfinance
            try:
                data = get_stock_data(stock_symbol)
            except:
                return Response({"error": "Faild to retrieve stock data"}, status=404)
            
            # filter for dates where closing price exceeds the given price
            result = data[data['Close'] > float(price)]

            # convert result to pandas DataFrame
            df = result.reset_index()[['Date', 'Close']]

            # create excel file
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df.to_excel(writer, index=False)
            writer.save()
            output.seek(0)

            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={stock_symbol}_stock_data.xlsx'
            return response
        
        return Response(serializer.errors, status=400)



