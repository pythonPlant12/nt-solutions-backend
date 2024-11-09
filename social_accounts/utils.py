from accounts.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
# Use special requests from google
from google.auth.transport import requests
# Use id_token from google.oauth2
from google.oauth2 import id_token


class Google():
    @staticmethod
    def validate(access_token):
        """Validate the token from google"""
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            # "verify that the token is issued by https://accounts.google.com"
            if "accounts.google.com" in id_info["iss"]:
                return id_info
        except Exception as e:
            return "Token is invalid or has expired."


def login_social_user(email):
    user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
    user_tokens = user.tokens()  # JWT tokens for user
    return {
        'email': user.email,
        'full_name': user.get_full_name,
        'access_token': str(user_tokens.get('access')),
        'refresh_token': str(user_tokens.get('refresh'))
    }


def register_social_user(provider, email, first_name, last_name):
    """Login or register a user using Google"""
    # First check if the user is already created with this credentials
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user.first().auth_provider:
            # If the user is already created with this provider, return the user with credentials as email and env password for Google
            auth_user = login_social_user(email)
        else:
            raise AuthenticationFailed(detail='Please continue your login using ' + user.first().auth_provider)
    else:
        new_user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_AUTH_PASSWORD,
            'auth_provider': provider,
            'is_verified': True  # User registered from Google is already verified
        }
        register_user = User.objects.create(**new_user)
        auth_user = login_social_user(email)
