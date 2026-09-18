from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    two_factor_enabled = serializers.BooleanField(read_only=True)

    class Meta:
        model=User
        fields=['id','username','email','first_name','last_name','is_staff','is_active','password','two_factor_enabled']
        extra_kwargs = {'password': {'write_only': True}}
