from rest_framework import viewsets

from .models import TestApp
from .serializers import TestAppSerializer


# Create your views here.
class TestAppViewSet(viewsets.ModelViewSet):
    queryset = TestApp.objects.all().order_by('-created_at')
    serializer_class = TestAppSerializer
