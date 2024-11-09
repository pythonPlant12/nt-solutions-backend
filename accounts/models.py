from django.db import models
# To create base class for the User and add permission management
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import OneToOneField
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .manager import UserManager

AUTH_PROVIDERS = {'email': 'email', 'google': 'google', 'facebook': 'facebook', 'github': 'github'}


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name=_("Email Address"), error_messages={"unique": _("Ya existe un usuario con este correo electrónico.")})
    first_name = models.CharField(max_length=255, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last Name"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    # Adding a field for auth_provider in case it is registered with a social media account
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        """In my case, I'm using the drf_simplejwt library to generate tokens and I'll generate them manually so I can
         attach some data to the token"""
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class OneTimePassword(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.first_name}-OTP-passcode"
