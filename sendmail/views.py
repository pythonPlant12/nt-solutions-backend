from rest_framework import viewsets
from rest_framework.response import Response

from utils.send_email_template import send_email_template
from .models import SendMail
from .serializers import SendMailSerializer

from django.conf import settings


# Create your views here.
class SendMailViewSet(viewsets.ModelViewSet):
    queryset = SendMail.objects.all().order_by('-datetime_sent')
    serializer_class = SendMailSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        try:
            context = request.data
            # send_mail("Contacto desde nt-solutions.es", str(request.data), "pythonplant12@gmail.com",
            #           ["nikitalutsai@gmail.com"])
            send_email_template("contact_form", "Contacto NT Solutions", context, "pythonplant12@gmail.com")
            super().create(request, *args, **kwargs)
            return Response({"message": "EMAIL ENVIADO DESDE try:"}, )

        except Exception as e:
            print("EMAIL ENVIADO DESDE except:", e)
            super().create(request, *args, **kwargs)
            return Response({"message": "EMAIL ENVIADO DESDE except:"}, )
