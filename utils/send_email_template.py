import random
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
# from django.utils.html import strip_tags


def send_email_template(template_name, subject, context, to_email):
    """
    Utility function to send templated emails
    """
    email_body = render_to_string(f'email_components/{template_name}.html', context)

    email_to_send = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.EMAIL_DEFAULT_FROM,
        to=[to_email]
    )
    email_to_send.content_subtype = "html"

    try:
        email_to_send.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
