import hmac

import pyotp
from django.core import signing
from django.db import transaction
from django.contrib.auth.hashers import check_password
from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError, Throttled
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from users.models import User
from users.api.authentication import VersionedTokenRefreshSerializer
from users.two_factor import (
    clear_failures, decrypt_secret, encrypt_secret, failed_code, issue_tokens, locked,
    new_recovery_codes, password_tag, provisioning_qr, verify_code,
)


LOGIN_SALT = 'censo-login-two-factor'
SETUP_SALT = 'censo-setup-two-factor'


class NoStoreMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response


class LoginView(NoStoreMixin, APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        if not user.two_factor_enabled:
            return Response(issue_tokens(user))
        challenge = signing.dumps({
            'uid': user.pk, 'version': user.auth_version,
            'password_tag': password_tag(user),
        }, salt=LOGIN_SALT)
        return Response({'requires_2fa': True, 'challenge_token': challenge})


class VerifyLoginView(NoStoreMixin, APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'

    def post(self, request):
        token = request.data.get('challenge_token', '')
        if not isinstance(token, str):
            raise AuthenticationFailed('El desafio no es valido.')
        try:
            challenge = signing.loads(token, salt=LOGIN_SALT, max_age=300)
        except signing.BadSignature:
            raise AuthenticationFailed('El desafio ha vencido. Inicia sesion de nuevo.')
        with transaction.atomic():
            user = User.objects.select_for_update().filter(pk=challenge.get('uid'), is_active=True).first()
            if not user or not user.two_factor_enabled or user.auth_version != challenge.get('version') or not hmac.compare_digest(password_tag(user), challenge.get('password_tag', '')):
                raise AuthenticationFailed('El desafio ha vencido. Inicia sesion de nuevo.')
            if locked(user):
                raise Throttled(detail='Demasiados intentos. Espera cinco minutos.')
            if not verify_code(user, request.data.get('code')):
                failed_code(user)
                return Response({'code': 'Codigo incorrecto o ya utilizado.'}, status=status.HTTP_400_BAD_REQUEST)
            clear_failures(user)
            user.save(update_fields=['totp_last_counter', 'recovery_code_hashes', 'otp_failed_attempts', 'otp_locked_until'])
            tokens = issue_tokens(user)
        return Response(tokens)


class TwoFactorSetupView(NoStoreMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'

    def post(self, request):
        user = request.user
        if user.two_factor_enabled:
            raise ValidationError({'detail': 'El segundo factor ya esta activo.'})
        secret = pyotp.random_base32()
        setup_token = signing.dumps({
            'uid': user.pk, 'version': user.auth_version, 'secret': encrypt_secret(secret),
        }, salt=SETUP_SALT)
        return Response({
            'setup_token': setup_token, 'secret': secret,
            'qr_code': provisioning_qr(secret, user.email),
        })


class TwoFactorConfirmView(NoStoreMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'

    def post(self, request):
        token = request.data.get('setup_token', '')
        if not isinstance(token, str):
            raise ValidationError({'detail': 'La configuracion no es valida.'})
        try:
            setup = signing.loads(token, salt=SETUP_SALT, max_age=600)
        except signing.BadSignature:
            raise ValidationError({'detail': 'La configuracion ha vencido. Genera un QR nuevo.'})
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=request.user.pk)
            if user.two_factor_enabled or setup.get('uid') != user.pk or setup.get('version') != user.auth_version:
                raise ValidationError({'detail': 'La configuracion ya no es valida.'})
            if not check_password(request.data.get('password', ''), user.password):
                raise ValidationError({'password': 'Contrasena incorrecta.'})
            if locked(user):
                raise Throttled(detail='Demasiados intentos. Espera cinco minutos.')
            encrypted = setup['secret']
            if not verify_code(user, request.data.get('code'), secret=decrypt_secret(encrypted), allow_recovery=False):
                failed_code(user)
                return Response({'code': 'Codigo incorrecto o ya utilizado.'}, status=status.HTTP_400_BAD_REQUEST)
            recovery_codes, hashes = new_recovery_codes()
            user.totp_secret = encrypted
            user.recovery_code_hashes = hashes
            user.auth_version += 1
            clear_failures(user)
            user.save(update_fields=[
                'totp_secret', 'totp_last_counter', 'recovery_code_hashes',
                'auth_version', 'otp_failed_attempts', 'otp_locked_until',
            ])
            tokens = issue_tokens(user)
        return Response({**tokens, 'recovery_codes': recovery_codes, 'two_factor_enabled': True})


class TwoFactorDisableView(NoStoreMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'

    def post(self, request):
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=request.user.pk)
            if not user.two_factor_enabled:
                raise ValidationError({'detail': 'El segundo factor no esta activo.'})
            if not check_password(request.data.get('password', ''), user.password):
                raise ValidationError({'password': 'Contrasena incorrecta.'})
            if locked(user):
                raise Throttled(detail='Demasiados intentos. Espera cinco minutos.')
            if not verify_code(user, request.data.get('code')):
                failed_code(user)
                return Response({'code': 'Codigo incorrecto o ya utilizado.'}, status=status.HTTP_400_BAD_REQUEST)
            user.totp_secret = ''
            user.totp_last_counter = -1
            user.recovery_code_hashes = []
            user.auth_version += 1
            clear_failures(user)
            user.save(update_fields=[
                'totp_secret', 'totp_last_counter', 'recovery_code_hashes',
                'auth_version', 'otp_failed_attempts', 'otp_locked_until',
            ])
            tokens = issue_tokens(user)
        return Response({**tokens, 'two_factor_enabled': False})


class VersionedTokenRefreshView(NoStoreMixin, TokenRefreshView):
    serializer_class = VersionedTokenRefreshSerializer
