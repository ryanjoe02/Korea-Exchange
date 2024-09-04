from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny

from datetime import datetime, timedelta

from .models import KospiData
from .serializers import KospiDataSerializer,CustomTokenCreateSerializer

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