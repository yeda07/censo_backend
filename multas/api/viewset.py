from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from multas.models import Multa
from multas.api.serializers import MultaSerializer


class MultaViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=MultaSerializer
    queryset=Multa.objects.all()