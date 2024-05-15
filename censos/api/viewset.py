from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from censos.models import Censo
from censos.api.serializers import CensoSerializer


class CensoViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=CensoSerializer
    queryset=Censo.objects.all()