from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime, timedelta

from .models import KospiData
from .serializers import KospiDataSerializer

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