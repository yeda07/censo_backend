from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from familias.models import Familia
from familias.api.serializers import FamiliaSerializer


class FamiliaViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=FamiliaSerializer
    queryset=Familia.objects.all()