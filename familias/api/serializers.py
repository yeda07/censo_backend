from rest_framework import serializers
from django.db import transaction

from familias.models import Familia, MetaCensoFamiliar


class MetaCensoFamiliarSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaCensoFamiliar
        fields = ['vigencia', 'integrantes_previstos']


class FamiliaSerializer(serializers.ModelSerializer):
    metas_censo = MetaCensoFamiliarSerializer(many=True, read_only=True)
    vigencia = serializers.CharField(write_only=True, required=False, allow_blank=False)
    integrantes_previstos = serializers.IntegerField(write_only=True, required=False, min_value=1)

    class Meta:
        model=Familia
        fields=['id','numero_familia','nombre_flia','vigencia','integrantes_previstos','metas_censo']

    def validate(self, attrs):
        if ('vigencia' in attrs) != ('integrantes_previstos' in attrs):
            raise serializers.ValidationError('Vigencia e integrantes previstos deben enviarse juntos.')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        vigencia = validated_data.pop('vigencia', None)
        previstos = validated_data.pop('integrantes_previstos', None)
        familia = Familia.objects.create(**validated_data)
        if vigencia is not None:
            MetaCensoFamiliar.objects.create(
                familia=familia, vigencia=vigencia, integrantes_previstos=previstos,
            )
        return familia

    @transaction.atomic
    def update(self, instance, validated_data):
        vigencia = validated_data.pop('vigencia', None)
        previstos = validated_data.pop('integrantes_previstos', None)
        familia = super().update(instance, validated_data)
        if vigencia is not None:
            MetaCensoFamiliar.objects.update_or_create(
                familia=familia, vigencia=vigencia,
                defaults={'integrantes_previstos': previstos},
            )
        return familia
