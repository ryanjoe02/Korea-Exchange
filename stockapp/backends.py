from typing import Optional, Any
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

User = get_user_model()


# The "authenticate" function by default attempts authentication using the username
# If you want to authenticate using email, an email-based authentication backend needs to be configured
class EmailBackend(ModelBackend):
    def authenticate(self, request: HttpRequest, email: Optional[str] = None, password: Optional[str] = None, **kwargs: Any) -> Optional[AbstractBaseUser]:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
        if user.check_password(password):
            return user
        
        return None
