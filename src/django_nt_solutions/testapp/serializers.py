from rest_framework import serializers
from testapp.models import TestApp


class TestAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestApp
        fields = '__all__'
