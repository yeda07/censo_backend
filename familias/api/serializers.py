from rest_framework import serializers
from familias.models import Familia


class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Familia
        fields=['id','numero_familia','nombre_flia']