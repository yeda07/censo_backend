from rest_framework import serializers
from personas.models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Persona
        fields = [
            'id',
            'familida_id',
            'nombres',
            'apellidos',
            'tipo_documento',
            'numero_documento',
            'exp_documento',
            'fecha_nacimiento',
            'parentesco',
            'sexo',
            'estado_civil',
            'profesion',
            'escolaridad',
            'integrantes',
            'direccion',
            'telefono',
            'usuario',
        ]