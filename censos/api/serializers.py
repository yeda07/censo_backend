from rest_framework import serializers
from censos.models import Censo
from personas.api.serializers import PersonaSerializer
from personas.models import Persona


class CensoSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()  # Serializador anidado de Persona

    class Meta:
        model = Censo
        fields = ['vigencia', 'resguardo_ind', 'comunidad_ind', 'persona']

    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        persona = Persona.objects.create(**persona_data)
        censo = Censo.objects.create(persona=persona, **validated_data)
        return censo