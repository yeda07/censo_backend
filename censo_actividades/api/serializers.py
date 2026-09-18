from rest_framework import serializers

from censo_actividades.models import CensoActividad
from censo_actividades.services import confirmar_actividad_realizada
from multas.api.serializers import MultaSerializer


class CensoActSerializer(serializers.ModelSerializer):
    multas = MultaSerializer(many=True, read_only=True)
    fecha_realizacion = serializers.DateField(read_only=True)

    class Meta:
        model = CensoActividad
        fields = ['id', 'censo', 'actividad', 'estado', 'fecha_realizacion', 'multas']

    def validate(self, attrs):
        estado = attrs.get('estado', self.instance.estado if self.instance else CensoActividad.PENDIENTE)
        if self.instance is None and (not attrs.get('censo') or not attrs.get('actividad')):
            raise serializers.ValidationError('Se requiere censo y actividad.')
        if self.instance and any(
            field in attrs and attrs[field] != getattr(self.instance, field)
            for field in ('censo', 'actividad')
        ):
            raise serializers.ValidationError('No se puede cambiar el censo o la actividad asignada.')
        if self.instance is None and estado != CensoActividad.PENDIENTE:
            raise serializers.ValidationError({'estado': 'Una actividad nueva inicia pendiente.'})
        if self.instance and estado == CensoActividad.NO_REALIZADA:
            raise serializers.ValidationError({'estado': 'El vencimiento se calcula automaticamente.'})
        if self.instance and self.instance.estado == CensoActividad.NO_REALIZADA and estado != CensoActividad.TERMINADA:
            raise serializers.ValidationError({'estado': 'Una actividad vencida solo puede marcarse realizada.'})
        if self.instance and self.instance.estado == CensoActividad.TERMINADA and estado != CensoActividad.TERMINADA:
            raise serializers.ValidationError({'estado': 'Una actividad realizada no puede volver a pendiente.'})
        if self.instance and 'estado' in attrs and estado != self.instance.estado and estado != CensoActividad.TERMINADA:
            raise serializers.ValidationError({'estado': 'Solo se puede confirmar una actividad como realizada.'})
        return attrs

    def update(self, instance, validated_data):
        if validated_data.get('estado') == CensoActividad.TERMINADA and instance.estado != CensoActividad.TERMINADA:
            return confirmar_actividad_realizada(instance)
        return super().update(instance, validated_data)
