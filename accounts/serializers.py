from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from accounts.models import User
from accounts.utils import send_normal_email


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    default_error_messages = {
        'email': 'Ya existe un usuario con este correo electrónico'
    }

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        # TODO: Confirm if the return statement is correct or is needed to use super().validate(attrs)
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
        # return super().validate(attrs)

    def create(self, validated_data):
        # TODO: Confirm if the return statement is correct or is needed to use super().create(validated_data)
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
        # return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('Las credenciales no son válidas, intente de nuevo')
        if not user.is_verified:
            raise AuthenticationFailed('Correo electrónico no está verificado')
        user_tokens = user.tokens()
        # TODO: This can be improved by adding this information directly to the token
        return {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        # TODO:Can be improven to not making two requests
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Generate urlsafe user id
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            # Generate token for password reset
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            # Get the domain of the frontend app
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            # TODO: Change http to https in production
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"Hi, use the link below to reset your password \n{abslink}"
            data = {
                'email_body': email_body,
                'email_subject': 'Reset your password',
                'to_email': user.email
            }
            send_normal_email(data)
            return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            # Validations for the password reset
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Reset link is invalid or expired.', 401)
            if password != confirm_password:
                raise AuthenticationFailed('Passwords do not match.', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise AuthenticationFailed('Reset link is invalid or expired.', 401)


class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    default_error_messages = {
        'bad_token': 'Token is invalid or expired'
    }

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.refresh_token)
            refresh_token.blacklist()
        except TokenError:
            # Return ValidationError with a key of: bad_token which then will return an error value from our key in default_error_messages
            return self.fail('bad_token')
