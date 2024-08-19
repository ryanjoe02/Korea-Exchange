from rest_framework import serializers
from .models import KospiData

class KospiDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = KospiData
        fields = '__all__'