from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from actividades.models import Actividad
from actividades.api.serializers import ActividadSerializer


class ActividadViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=ActividadSerializer
    queryset=Actividad.objects.all()