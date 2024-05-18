from rest_framework import serializers
from censo_actividades.models import CensoActividad


class CensoActSerializer(serializers.ModelSerializer):

    class Meta:
        model = CensoActividad
        fields = ['id', 'censo', 'actividad', 'estado']
