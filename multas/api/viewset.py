from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from multas.models import Multa
from multas.api.serializers import MultaSerializer


class MultaViewSet(ReadOnlyModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=MultaSerializer
    queryset=Multa.objects.all()
