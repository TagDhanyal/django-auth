from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import mail


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_user(self):
        # Send a POST request to the register endpoint
        response = self.client.post(self.register_url, {'email': 'test@example.com', 'password': 'testpassword'})

        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the user is created in the database
        User = get_user_model()
        user_exists = User.objects.filter(email='test@example.com').exists()
        self.assertTrue(user_exists)

    def test_register_invalid_data(self):
        # Send a POST request with invalid data
        response = self.client.post(self.register_url, {'email': 'invalid-email', 'password': ''})

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the user is not created in the database
        User = get_user_model()
        user_exists = User.objects.filter(email='invalid-email').exists()
        self.assertFalse(user_exists)

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        # Create a user for testing
        User = get_user_model()
        self.user = User.objects.create_user(email='test@example.com', password='testpassword')

    def test_login_user(self):
        # Send a POST request to the login endpoint
        response = self.client.post(self.login_url, {'email': 'test@example.com', 'password': 'testpassword'})

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the JWT token is present in the response
        self.assertIn('jwt', response.data)

    def test_login_invalid_credentials(self):
        # Send a POST request with invalid credentials
        response = self.client.post(self.login_url, {'email': 'test@example.com', 'password': 'wrongpassword'})

        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Assert that the JWT token is not present in the response
        self.assertNotIn('jwt', response.data)

class ForgotPasswordAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.forgot_password_url = reverse('forgot-password')

    def test_forgot_password(self):
        # Send a POST request to the forgot password endpoint
        response = self.client.post(self.forgot_password_url, {'email': 'test@example.com'})

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the expected message is returned in the response
        self.assertEqual(response.data['message'], 'Please check your email to reset your password')

        # Assert that an email is sent to the user
        self.assertEqual(len(mail.outbox), 1)

        # Assert that the email contains the expected subject
        self.assertEqual(mail.outbox[0].subject, 'Reset Your Password')

        # Assert that the email contains the reset URL
        self.assertIn('Please click the link', mail.outbox[0].body)
        self.assertIn('http://localhost:8080/reset/', mail.outbox[0].body)

    def test_forgot_password_invalid_email(self):
        # Send a POST request with an invalid email address
        response = self.client.post(self.forgot_password_url, {'email': 'invalid-email'})

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the expected error message is returned in the response
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

        # Assert that no email is sent to the user
        self.assertEqual(len(mail.outbox), 0)
