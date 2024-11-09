import random
from django.core.mail import EmailMessage
from django.conf import settings

from accounts.models import User, OneTimePassword
from django_nt_solutions.settings import env
from utils.send_email_template import send_email_template


# TODO: This is the most basic OTP creator function, but it should be improved with a PyOTP library
def generate_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(1, 9))
    return otp


def send_code_to_user(email, encoded_email):
    subject = "Confirma tu correo electrónico"
    otp_code = generate_otp()
    user = User.objects.get(email=email)
    current_site = "nt-solutions.es"

    # Context for email templates
    context = {
        'user': user,
        'site_name': current_site,
        'otp_code': otp_code,
        'verification_url': f"{env('FRONTEND_URL')}/verify-user/{encoded_email}/",
    }

    OneTimePassword.objects.create(user=user, code=otp_code)
    send_email_template("email_verification", subject, context, email)


def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
