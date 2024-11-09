from rest_framework import serializers
from .utils import Google, register_social_user
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=6)

    def validate_access_token(self, access_token):
        google_user_data = Google.validate(access_token)
        try:
            user_id = google_user_data["sub"]

        except:
            raise serializers.ValidationError("This token is invalid or expired. Please login again.")

        # Check that this request is not coming from a malicious app
        if google_user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("Could not verify user.")

        email = google_user_data["email"]
        first_name = google_user_data["given_name"] # This key is coming from google
        last_name = google_user_data["family_name"]
        provider = "google"
        return register_social_user(provider, email, first_name, last_name)

