from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Please enter a valid email address"))

    def create_user(self, email, first_name, last_name, password, **extra_fields):
        # Checks for creating user
        if email:
            email = self.normalize_email(email)
            self.email_validator(email=email)
        else:
            raise ValueError(_("The email address is required"))

        if not first_name:
            raise ValueError(_("The first name is required"))

        if not last_name:
            raise ValueError(_("The last name is required"))

        # Setting fields with values
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        # This will create a hashed password, save and return the user
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        # Adding some extra fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        # Validations for superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Is staff must be true for the superuser"))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Is superuser must be true for the superuser"))

        # Create, save and return superuser
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.save(using=self._db)
        return user
