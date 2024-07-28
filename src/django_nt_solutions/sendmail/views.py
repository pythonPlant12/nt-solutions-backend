from rest_framework import viewsets
from rest_framework.response import Response

from .models import SendMail
from .serializers import SendMailSerializer

from django.conf import settings
from django.core.mail import send_mail


# Create your views here.
class SendMailViewSet(viewsets.ModelViewSet):
    queryset = SendMail.objects.all().order_by('-datetime_sent')
    serializer_class = SendMailSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        send_mail("Contacto desde nt-solutions.es", str(request.data), "pythonplant12@gmail.com",
                  ["nikitalutsai@gmail.com"])
        return super().create(request, *args, **kwargs)
