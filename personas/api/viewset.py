from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from personas.models import Persona
from personas.api.serializers import PersonaSerializer


class PersonaViewSet(ModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=PersonaSerializer
    queryset=Persona.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        familia_id = self.request.query_params.get('familia_id')
        if familia_id is None:
            return queryset
        try:
            familia_id = int(familia_id)
        except ValueError as error:
            raise ValidationError({'familia_id': 'Debe ser un numero entero.'}) from error
        return queryset.filter(familida_id_id=familia_id)
