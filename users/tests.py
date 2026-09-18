from time import time

import pyotp
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from users.models import User


class TwoFactorTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='operator', email='operator@example.test', password='TestPassword123!',
        )
        self.client = APIClient()

    def login(self, path='/api/token/'):
        return self.client.post(path, {
            'email': self.user.email, 'password': 'TestPassword123!',
        }, format='json')

    def authorize(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def setup(self):
        original = self.login()
        self.assertEqual(original.status_code, 200)
        self.authorize(original.data['access'])
        setup = self.client.post('/auth/2fa/setup/')
        self.assertEqual(setup.status_code, 200)
        self.assertEqual(setup['Cache-Control'], 'no-store')
        self.assertTrue(setup.data['qr_code'].startswith('data:image/png;base64,'))
        code = pyotp.TOTP(setup.data['secret']).now()
        confirmed = self.client.post('/auth/2fa/confirm/', {
            'setup_token': setup.data['setup_token'], 'password': 'TestPassword123!', 'code': code,
        }, format='json')
        self.assertEqual(confirmed.status_code, 200)
        return original.data, setup.data, confirmed.data

    def test_login_requires_second_factor_and_revokes_old_tokens(self):
        old, setup, confirmed = self.setup()
        self.assertEqual(len(confirmed['recovery_codes']), 8)
        self.assertEqual(self.client.get('/auth/me/').status_code, 401)
        self.assertEqual(self.client.post('/api/token/refresh/', {'refresh': old['refresh']}).status_code, 401)

        self.client.credentials()
        challenge = self.login()
        self.assertEqual(challenge.status_code, 200)
        self.assertTrue(challenge.data['requires_2fa'])
        self.assertNotIn('access', challenge.data)
        self.assertNotIn('refresh', challenge.data)
        self.assertEqual(self.login('/auth/login/').status_code, 404)

        wrong = self.client.post('/api/token/verify/', {
            'challenge_token': challenge.data['challenge_token'], 'code': '000000',
        }, format='json')
        self.assertEqual(wrong.status_code, 400)
        next_code = pyotp.TOTP(setup['secret']).at(time() + 30)
        verified = self.client.post('/api/token/verify/', {
            'challenge_token': challenge.data['challenge_token'], 'code': next_code,
        }, format='json')
        self.assertEqual(verified.status_code, 200)
        self.assertIn('access', verified.data)
        replay = self.client.post('/api/token/verify/', {
            'challenge_token': challenge.data['challenge_token'], 'code': next_code,
        }, format='json')
        self.assertEqual(replay.status_code, 400)
        self.authorize(verified.data['access'])
        profile = self.client.get('/auth/me/')
        self.assertTrue(profile.data['two_factor_enabled'])
        self.assertNotIn('totp_secret', profile.data)
        self.assertNotIn('recovery_code_hashes', profile.data)

    def test_recovery_code_is_single_use_and_disable_requires_password(self):
        _, _, confirmed = self.setup()
        self.authorize(confirmed['access'])
        recovery = confirmed['recovery_codes'][0]
        bad_password = self.client.post('/auth/2fa/disable/', {
            'password': 'wrong', 'code': recovery,
        }, format='json')
        self.assertEqual(bad_password.status_code, 400)
        disabled = self.client.post('/auth/2fa/disable/', {
            'password': 'TestPassword123!', 'code': recovery,
        }, format='json')
        self.assertEqual(disabled.status_code, 200)
        self.assertFalse(disabled.data['two_factor_enabled'])
        self.assertEqual(self.client.get('/auth/me/').status_code, 401)
        self.assertEqual(self.client.post('/api/token/refresh/', {'refresh': confirmed['refresh']}).status_code, 401)
        self.authorize(disabled.data['access'])
        self.assertFalse(self.client.get('/auth/me/').data['two_factor_enabled'])
        self.client.credentials()
        self.assertIn('access', self.login().data)

    def test_failed_otp_attempts_lock_login(self):
        _, _, confirmed = self.setup()
        self.client.credentials()
        challenge = self.login().data['challenge_token']
        for _ in range(5):
            response = self.client.post('/api/token/verify/', {
                'challenge_token': challenge, 'code': 'invalid',
            }, format='json')
            self.assertEqual(response.status_code, 400)
        locked = self.client.post('/api/token/verify/', {
            'challenge_token': challenge, 'code': confirmed['recovery_codes'][0],
        }, format='json')
        self.assertEqual(locked.status_code, 429)

    def test_recovery_code_cannot_be_reused_at_login(self):
        _, _, confirmed = self.setup()
        self.client.credentials()
        challenge = self.login().data['challenge_token']
        code = confirmed['recovery_codes'][0]
        first = self.client.post('/api/token/verify/', {
            'challenge_token': challenge, 'code': code,
        }, format='json')
        self.assertEqual(first.status_code, 200)
        second = self.client.post('/api/token/verify/', {
            'challenge_token': challenge, 'code': code,
        }, format='json')
        self.assertEqual(second.status_code, 400)

    def test_recovery_code_works_after_secret_key_rotation(self):
        _, _, confirmed = self.setup()
        self.client.credentials()
        with override_settings(SECRET_KEY='rotated-test-key'):
            challenge = self.login().data['challenge_token']
            result = self.client.post('/api/token/verify/', {
                'challenge_token': challenge, 'code': confirmed['recovery_codes'][0],
            }, format='json')
            self.assertEqual(result.status_code, 200)
