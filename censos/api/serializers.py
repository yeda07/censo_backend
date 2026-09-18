from rest_framework import serializers
from django.db import transaction
from censos.models import Censo
from personas.api.serializers import PersonaSerializer
from personas.models import Persona


class CensoSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(required=False)
    persona_id = serializers.PrimaryKeyRelatedField(
        source='persona', queryset=Persona.objects.all(), write_only=True, required=False
    )
    persona_data = PersonaSerializer(write_only=True, required=False)

    class Meta:
        model = Censo
        fields = ['id', 'vigencia', 'resguardo_ind', 'comunidad_ind', 'persona', 'persona_id', 'persona_data']

    def validate(self, attrs):
        if self.instance is None and 'persona' not in attrs:
            raise serializers.ValidationError({'persona_id': 'Seleccione una persona.'})
        if self.instance and 'persona' in attrs and isinstance(attrs['persona'], dict):
            raise serializers.ValidationError({'persona': 'Use persona_data para editar la persona.'})
        if 'persona_data' in attrs and not (
            isinstance(attrs.get('persona'), Persona) or (self.instance and self.instance.persona)
        ):
            raise serializers.ValidationError({'persona_data': 'Seleccione una persona existente.'})
        persona = attrs.get('persona', self.instance.persona if self.instance else None)
        if isinstance(persona, Persona):
            vigencia = attrs.get('vigencia', self.instance.vigencia if self.instance else None)
            duplicado = Censo.objects.filter(persona=persona, vigencia=vigencia)
            if self.instance:
                duplicado = duplicado.exclude(pk=self.instance.pk)
            if duplicado.exists():
                raise serializers.ValidationError({'vigencia': 'Esta persona ya tiene un censo en esa vigencia.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        persona_data = validated_data.pop('persona_data', None)
        persona = validated_data.pop('persona')
        if isinstance(persona, dict):
            persona = Persona.objects.create(**persona)
        elif persona_data:
            for field, value in persona_data.items():
                setattr(persona, field, value)
            persona.save()
        censo = Censo.objects.create(persona=persona, **validated_data)
        return censo

    @transaction.atomic
    def update(self, instance, validated_data):
        persona_data = validated_data.pop('persona_data', None)
        if persona_data:
            persona = validated_data.get('persona', instance.persona)
            for field, value in persona_data.items():
                setattr(persona, field, value)
            persona.save()
        return super().update(instance, validated_data)
