from rest_framework import serializers
from censo_actividades.models import CensoActividad
from multas.api.serializers import MultaSerializer
from multas.models import Multa


class CensoActSerializer(serializers.ModelSerializer):
    multa = MultaSerializer()

    class Meta:
        model = CensoActividad
        fields = ['censo', 'actividad', 'estado', 'multa']

    def create(self, validated_data):
        multa_data = validated_data.pop('multa', None)
        censo_actividad = CensoActividad.objects.create(**validated_data)
        if multa_data:
            Multa.objects.create(censo_actividad=censo_actividad, **multa_data)
        return censo_actividad

    def update(self, instance, validated_data):
        multa_data = validated_data.pop('multa', None)
        instance.censo = validated_data.get('censo', instance.censo)
        instance.actividad = validated_data.get('actividad', instance.actividad)
        instance.estado = validated_data.get('estado', instance.estado)
        instance.save()

        if multa_data:
            if instance.multa:
                instance.multa.monto = multa_data.get('monto', instance.multa.monto)
                instance.multa.fecha_pago = multa_data.get('fecha_pago', instance.multa.fecha_pago)
                instance.multa.save()
            else:
                Multa.objects.create(censo_actividad=instance, **multa_data)

        return instance