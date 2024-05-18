from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from censo_actividades.models import CensoActividad
from censo_actividades.api.serializers import CensoActSerializer


class CensoActViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=CensoActSerializer
    queryset=CensoActividad.objects.all()