import yfinance as yf
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime, timedelta

@api_view(['GET'])
def get_stock_close(request, date):
    try:
        # Convert the date (0809 -> 20240809)
        current_year = datetime.now().year
        full_date = datetime.strptime(f"{current_year}{date}", "%Y%m%d").strftime("%Y-%m-%d")
        
        # Fetch KOSPI index data using the correct ticker symbol
        kospi = yf.Ticker("^KS11")

        # Calcuate date, end_date must be start_date + 1
        start_date = datetime.strptime(full_date, "%Y-%m-%d")
        end_date = (start_date + timedelta(days=1)).strftime("%Y-%m-%d")

        # Retrieve the closing price (종가) for the given date
        data = kospi.history(start=start_date, end=end_date)
        
        # Ensure that data was returned
        if data.empty:
            return Response({'error': 'No data found for the specified date.'}, status=404)

        close_price = data['Close'].iloc[0]

        # Round to two decimal places
        rounded_price = round(close_price, 2)
        
        # Return as JSON
        return Response({'date': full_date, 'close_price': rounded_price})

    except IndexError:
        return Response({'error': 'No data found for the specified date.'}, status=404)
    except ValueError:
        return Response({'error': 'Invalid date format.'}, status=400)
