from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import KospiData

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'username', 'password']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'username']

# custom login (username or email) and (password)
class CustomTokenCreateSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        if username_or_email and password:
            # Distingush between email and username
            if '@' in username_or_email:
                print(f"Trying to authenticate with email: {username_or_email}")
                user = authenticate(request=self.context.get('request'), email=username_or_email, password=password)
            else:
                print(f"Trying to authenticate with email: {username_or_email}")
                user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)

            if not user:
                print("Authentication failed. Invalid credentials.")
                raise serializers.ValidationError('Invalid credentials (only email and username)')
            else:
                print(f"authenticated user: {user}")
        else:
            raise serializers.ValidationError('Both fields are required')
        
        attrs['user'] = user
        return attrs

class KospiDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = KospiData
        fields = '__all__'
