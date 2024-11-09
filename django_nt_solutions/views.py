from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from utils.send_email_template import send_email_template


class NewsLetterView(GenericAPIView):
    def post(self, request):
        email = request.data.get('email')
        send_email_template('newsletter', '¡Gracias por suscribirte a nuestro boletín!', {'email': email}, email)
        return Response(status=status.HTTP_204_NO_CONTENT)
