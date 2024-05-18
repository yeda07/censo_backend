from rest_framework import serializers
from multas.models import Multa


class MultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Multa
        fields = ['id', 'censo_actividad', 'monto', 'pagada', 'fecha_pago']
