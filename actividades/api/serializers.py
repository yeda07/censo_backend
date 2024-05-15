from rest_framework import serializers
from actividades.models import Actividad

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model= Actividad
        fields=['id','descripcion','fecha_limite']