from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions

from censo_actividades.models import CensoActividad
from censo_actividades.api.serializers import CensoActSerializer
from censo_actividades.services import actualizar_actividades_vencidas


class CensoActViewSet(ModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=CensoActSerializer
    queryset=CensoActividad.objects.all()

    def get_queryset(self):
        actualizar_actividades_vencidas()
        return super().get_queryset().select_related('censo__persona', 'actividad').prefetch_related('multas')

    def perform_create(self, serializer):
        asignacion = serializer.save()
        actualizar_actividades_vencidas(censo_id=asignacion.censo_id)
        asignacion.refresh_from_db()
