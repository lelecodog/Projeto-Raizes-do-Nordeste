from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Pedidos",
        default_version='v1',
        description="Documentação da API de Pedidos",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="suporte@raizesdonordeste.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', lambda request: HttpResponseRedirect('/swagger/')),
    path('admin/', admin.site.urls),
    path('api/', include('pedidos.urls')),
    path("api/", include("autenticacao.urls")),

    # Rotas Swagger e ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

