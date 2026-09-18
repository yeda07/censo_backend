import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone as datetime_timezone
from io import BytesIO

import pyotp
import qrcode
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


def _cipher():
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt_secret(secret):
    return _cipher().encrypt(secret.encode()).decode()


def decrypt_secret(secret):
    return _cipher().decrypt(secret.encode()).decode()


def provisioning_qr(secret, email):
    uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name='Censo del resguardo')
    image = qrcode.make(uri)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()


def password_tag(user):
    return hmac.new(settings.SECRET_KEY.encode(), user.password.encode(), hashlib.sha256).hexdigest()


def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['auth_version'] = user.auth_version
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


def new_recovery_codes():
    codes = [secrets.token_hex(5).upper() for _ in range(8)]
    return codes, [make_password(code) for code in codes]


def locked(user):
    return bool(user.otp_locked_until and user.otp_locked_until > timezone.now())


def failed_code(user):
    user.otp_failed_attempts += 1
    if user.otp_failed_attempts >= 5:
        user.otp_locked_until = timezone.now() + timedelta(minutes=5)
        user.otp_failed_attempts = 0
    user.save(update_fields=['otp_failed_attempts', 'otp_locked_until'])


def clear_failures(user):
    user.otp_failed_attempts = 0
    user.otp_locked_until = None


def verify_code(user, raw_code, secret=None, allow_recovery=True):
    code = str(raw_code or '').strip().replace(' ', '').replace('-', '').upper()
    if not code:
        return False
    if len(code) == 6 and code.isascii() and code.isdigit():
        try:
            secret = secret or decrypt_secret(user.totp_secret)
        except InvalidToken:
            return False
        totp = pyotp.TOTP(secret)
        now = datetime.now(datetime_timezone.utc)
        current = totp.timecode(now)
        for counter in (current - 1, current, current + 1):
            if counter > user.totp_last_counter and counter >= 0:
                instant = datetime.fromtimestamp(counter * totp.interval, tz=datetime_timezone.utc)
                if totp.verify(code, for_time=instant):
                    user.totp_last_counter = counter
                    return True
    if allow_recovery:
        for index, hashed in enumerate(user.recovery_code_hashes):
            if check_password(code, hashed):
                user.recovery_code_hashes.pop(index)
                return True
    return False
