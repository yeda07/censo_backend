from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


def version_matches(token, user):
    return token.get('auth_version', 0) == user.auth_version


class VersionedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not version_matches(validated_token, user):
            raise AuthenticationFailed('La sesion ya no es valida.', code='session_revoked')
        return user


class VersionedTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        user = User.objects.filter(pk=refresh.get('user_id'), is_active=True).first()
        if not user or not version_matches(refresh, user):
            raise AuthenticationFailed('La sesion ya no es valida.', code='session_revoked')
        return super().validate(attrs)
