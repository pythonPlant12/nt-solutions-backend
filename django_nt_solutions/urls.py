from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django_nt_solutions.views import NewsLetterView
from sendmail.views import SendMailViewSet

# Configure schema view
schema_view = get_schema_view(
    openapi.Info(
        title="NT Solutions API",
        default_version='v1',
        description="This is the main backend of NT Solutions",
        contact=openapi.Contact(email="pythonplant12@gmail.com"),
    ),
    public=True,
)

router = routers.DefaultRouter()
router.register(r'send-contact-form', SendMailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/swagger-json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/v1/rest-framework/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/auth/', include('social_accounts.urls')),
    path('api/v1/newsletter/', NewsLetterView.as_view(), name='newsletter'),

]
