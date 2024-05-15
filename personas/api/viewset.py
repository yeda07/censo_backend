from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from personas.models import Persona
from personas.api.serializers import PersonaSerializer


class PersonaViewSet(ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class=PersonaSerializer
    queryset=Persona.objects.all()