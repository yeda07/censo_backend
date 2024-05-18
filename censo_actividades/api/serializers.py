from rest_framework import serializers
from censo_actividades.models import CensoActividad
from multas.api.serializers import MultaSerializer
from multas.models import Multa


class CensoActSerializer(serializers.ModelSerializer):
    multas = MultaSerializer(many=True, read_only=True)
    multa_monto = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    fecha_pago = serializers.DateField(write_only=True, required=False)  # Nuevo campo para capturar la fecha de pago

    class Meta:
        model = CensoActividad
        fields = ['id', 'censo', 'actividad', 'estado', 'multas', 'multa_monto', 'fecha_pago']

    def create(self, validated_data):
        multa_monto = validated_data.pop('multa_monto', None)
        fecha_pago = validated_data.pop('fecha_pago', None)
        
        censo_actividad = CensoActividad.objects.create(**validated_data)

        if validated_data.get('estado') == 'P':
            multa = Multa.objects.create(
                censo_actividad=censo_actividad, 
                monto=multa_monto or 100.00,
                pagada=bool(fecha_pago),
                fecha_pago=fecha_pago
            )

        return censo_actividad

    def update(self, instance, validated_data):
        estado = validated_data.get('estado', instance.estado)
        multa_monto = validated_data.pop('multa_monto', None)
        fecha_pago = validated_data.pop('fecha_pago', None)

        if estado == 'P' and instance.estado != 'P':
            Multa.objects.get_or_create(censo_actividad=instance, defaults={'monto': multa_monto or 50000.00})
        
        if fecha_pago and estado == 'P':
            multa = Multa.objects.filter(censo_actividad=instance, pagada=False).first()
            if multa:
                multa.pagada = True
                multa.fecha_pago = fecha_pago
                multa.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
