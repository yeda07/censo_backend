
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

...
from django.views.static import serve

from django.contrib import admin
from django.urls import include, path
from personas.api.router import route_persona
from familias.api.router import route_familia
from actividades.api.router import route_actividad
from censos.api.router import route_censo
from censo_actividades.api.router import route_censo_act
from multas.api.router import route_multa
from users.api.router import route_user
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="cabildo API",
        default_version='v1',
        description="apicabildo",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('',include(route_persona.urls)),
    path('',include(route_familia.urls)),
    path('',include(route_actividad.urls)),
    path('',include(route_censo.urls)),
    path('',include(route_censo_act.urls)),
    path('',include(route_multa.urls)),
    path('',include(route_user.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns +=[
    re_path(r'^media/(?P<path>.*)$',serve,{
        'document_root': settings.MEDIA_ROOT
    })
]
