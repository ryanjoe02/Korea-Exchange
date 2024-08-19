from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import KospiData
from .serializers import KospiDataSerializer
from datetime import datetime, timedelta

@api_view(['GET'])
def latest_kospi_data(request):
    fifty_days = datetime.now().date() - timedelta(days=50)
    latest_data = KospiData.objects.filter(date__gte=fifty_days).order_by('-date')
    serializer = KospiDataSerializer(latest_data, many=True)

    return Response(serializer.data)