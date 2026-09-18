from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.test',
            password='TestPassword123!',
        )
        self.client = APIClient()

    def test_censo_requires_jwt(self):
        self.assertEqual(self.client.get('/censo/').status_code, 401)

        token_response = self.client.post(
            '/api/token/',
            {'email': self.user.email, 'password': 'TestPassword123!'},
            format='json',
        )
        self.assertEqual(token_response.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
        self.assertEqual(self.client.get('/censo/').status_code, 200)

        users_response = self.client.get('/users/')
        self.assertEqual(users_response.status_code, 200)
        self.assertNotIn('password', users_response.data[0])
