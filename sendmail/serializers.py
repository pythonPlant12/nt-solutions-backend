from rest_framework import serializers

from .models import SendMail


class SendMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendMail
        fields = '__all__'
