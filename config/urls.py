from django.conf import settings
from django.core.asgi import get_asgi_application 
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from courses.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ['http', 'https']
        return schema
        
        
schema_view = get_schema_view(
    openapi.Info(
        title="Education API",
        default_version='v1',
        description="swagger for AYITI",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/tests/', include('tests.urls')),
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
