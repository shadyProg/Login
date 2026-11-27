import re

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APIClient


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        mail.outbox = []
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePassword123!',
            is_active=True,
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

    def test_registration_requires_email_verification_before_login(self):
        registration_response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePassword123!',
        })

        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(get_user_model().objects.get(email='new@example.com').is_active)
        self.assertEqual(len(mail.outbox), 1)
        code = re.search(r'\b\d{5}\b', mail.outbox[0].body).group()

        login_before_verification = self.client.post(self.url, {
            'username': 'new@example.com',
            'password': 'SecurePassword123!',
        })
        self.assertEqual(
            login_before_verification.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn('Verify your email', str(login_before_verification.data['detail']))

        verification_response = self.client.post('/api/verify-email/', {
            'email': 'new@example.com',
            'code': code,
        })
        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        self.assertTrue(get_user_model().objects.get(email='new@example.com').is_active)

        login_response = self.client.post(self.url, {
            'username': 'new@example.com',
            'password': 'SecurePassword123!',
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_email_verification_rejects_an_invalid_code(self):
        registration_response = self.client.post('/api/register/', {
            'username': 'pendinguser',
            'email': 'pending@example.com',
            'password': 'SecurePassword123!',
        })
        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)

        sent_code = re.search(r'\b\d{5}\b', mail.outbox[0].body).group()
        wrong_code = f'{(int(sent_code) + 1) % 100000:05d}'
        response = self.client.post('/api/verify-email/', {
            'email': 'pending@example.com',
            'code': wrong_code,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            get_user_model().objects.get(email='pending@example.com').is_active
        )

    def test_resend_otp_sends_a_fresh_code_for_an_unverified_account(self):
        registration_response = self.client.post('/api/register/', {
            'username': 'resenduser',
            'email': 'resend@example.com',
            'password': 'SecurePassword123!',
        })
        self.assertEqual(registration_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/resend_otp/', {
            'email': 'resend@example.com',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        resent_code = re.search(r'\b\d{5}\b', mail.outbox[1].body).group()

        verification_response = self.client.post('/api/verify-email/', {
            'email': 'resend@example.com',
            'code': resent_code,
        })
        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            get_user_model().objects.get(email='resend@example.com').is_active
        )

    def test_resend_otp_does_not_disclose_unknown_emails(self):
        response = self.client.post('/api/resend_otp/', {
            'email': 'unknown@example.com',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {'detail': 'If the account is unverified, a new code has been sent.'},
        )
        self.assertEqual(len(mail.outbox), 0)


class SwaggerSchemaTests(TestCase):
    def test_registration_api_is_documented_and_swagger_ui_is_available(self):
        schema_response = self.client.get('/api/schema/')
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)

        register_operation = schema_response.data['paths']['/api/register/']['post']
        self.assertEqual(register_operation['operationId'], 'users_register_create')
        self.assertIn('requestBody', register_operation)
        self.assertIn('201', register_operation['responses'])
        verify_operation = schema_response.data['paths']['/api/verify-email/']['post']
        self.assertEqual(verify_operation['operationId'], 'users_verify_email_create')
        self.assertIn('requestBody', verify_operation)
        resend_operation = schema_response.data['paths']['/api/resend_otp/']['post']
        self.assertEqual(resend_operation['operationId'], 'users_resend_otp_create')
        self.assertIn('requestBody', resend_operation)

        docs_response = self.client.get('/api/docs/')
        self.assertEqual(docs_response.status_code, status.HTTP_200_OK)
