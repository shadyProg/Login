from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePassword123!',
        )
        self.url = '/api/login/'

    def test_login_with_username_returns_jwt_tokens(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'SecurePassword123!',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_email_returns_jwt_tokens(self):
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'SecurePassword123!',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_password_is_rejected(self):
        response = self.client.post(self.url, {
            'username': 'test@example.com',
            'password': 'incorrect',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registered_user_can_log_in_without_exposing_password(self):
        registration_response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePassword123!',
        })

        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', registration_response.data['user'])

        login_response = self.client.post(self.url, {
            'username': 'new@example.com',
            'password': 'SecurePassword123!',
        })

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)


class SwaggerSchemaTests(TestCase):
    def test_registration_api_is_documented_and_swagger_ui_is_available(self):
        schema_response = self.client.get('/api/schema/')
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)

        register_operation = schema_response.data['paths']['/api/register/']['post']
        self.assertEqual(register_operation['operationId'], 'users_register_create')
        self.assertIn('requestBody', register_operation)
        self.assertIn('201', register_operation['responses'])

        docs_response = self.client.get('/api/docs/')
        self.assertEqual(docs_response.status_code, status.HTTP_200_OK)
