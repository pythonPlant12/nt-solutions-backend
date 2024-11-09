from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from utils.send_email_template import send_email_template
from .models import OneTimePassword, User
from .serializers import UserRegisterSerializer, LoginSerializer, PasswordResetRequestSerializer, \
    SetNewPasswordSerializer, LogoutUserSerializer
from .utils import send_code_to_user


# Register view with password
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        encoded_email = request.data.get('encodedEmail')
        request.data.pop('encodedEmail', None)
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            send_code_to_user(user['email'], encoded_email)
            first_name = user.get('first_name')
            return Response(
                {
                    'data': user,
                    'message': f'Hola, {first_name}, gracias por registrarse en NT Solutions.'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(APIView):
    # TODO: Refactor the view to not use the serializer_class
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code=otp)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                user_code_obj.delete()
                return Response({
                    'message': 'Correo electrónico verificado con éxito',
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'El codigo es inválido o el usuario ya ha confirmado su correo electrónico.'
            }, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'El código es inválido',
            }, status=status.HTTP_404_NOT_FOUND)


class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie('access_token', serializer.data['access_token'], max_age=310, samesite='Lax')
        response.set_cookie('refresh_token', serializer.data['refresh_token'], max_age=86400, samesite='Lax')
        return response


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'A link for reset your password has been sent to your email'},
                        status=status.HTTP_200_OK)


class PasswordResetConfirm(GenericAPIView):
    serializer_class = Serializer

    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'The token is not valid or has expired'},
                                status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credentials are valid', 'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response({'message': 'The token is not valid or has expired'},
                            status=status.HTTP_401_UNAUTHORIZED)


class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


class TestAuthenticationView(GenericAPIView):
    """This view is to test the authentication with JWT"""
    permission_classes = [IsAuthenticated]
    serializer_class = Serializer

    def get(self, request):
        data = {
            'msg': 'You are authenticated'
        }
        return Response(data, status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
