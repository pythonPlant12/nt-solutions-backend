from django.db import models


# Create your models here.
class SendMail(models.Model):
    name = models.CharField(max_length=100)
    phone = models.TextField(max_length=100)
    email = models.EmailField()
    requestType = models.CharField(max_length=100)
    companySize = models.CharField(max_length=100)
    texto = models.CharField(max_length=3000)
    datetime_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
