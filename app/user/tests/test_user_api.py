from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setup(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is seccessful"""
        payload = {
            'email': 'test@omain.com',
            'password': 'test123',
            'name': 'Test name'
        }

        apiresponse = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(apiresponse.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**apiresponse.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', apiresponse.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            'email': 'test@domain.com',
            'password': 'test123',
            'name': 'Test',
        }
        create_user(**payload)

        apiresponse = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(apiresponse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@domain.com',
            'password': 'te',
            'name': 'Test',
        }
        apiresponse = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(apiresponse.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def tet_create_token_user(self):
        """Test that a tokens is created for the user"""
        payload = {
            'email': 'test@domain.com',
            'password': 'test123'
        }
        """ To do this test first we create user for testing"""
        create_user(**payload)
        """We post our API url to make a request and we store the response in apiresponse"""
        apiresponse = self.client.post(TOKEN_URL, payload)

        """We check that there is a key called token is in the apiresponse.data"""
        self.assertIn('token', apiresponse.data)
        """Test that the response was a 200 OK"""
        self.assertEqual(apiresponse.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        """First of all we are starting create the user"""
        create_user(email='test@domain.com', password='test123')
        """We are creating payload with wrong informations, so we will have to response 400 Bad request"""
        payload = {
            'email': 'test@domain.com',
            'password': 'wrong'
        }
        apiresponse = self.client.post(TOKEN_URL, payload)
        """we check that there isn't any a key called token is int the response"""
        self.assertNotIn('token', apiresponse.data)
        """Test that the response was a 400 Bad request"""
        self.assertEqual(apiresponse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""
        payload = {
            'email': 'test@domain.com',
            'password': 'test123'
        }
        apiresponse = self.client.post(TOKEN_URL, payload)
        """In this test we didn't create user and we request to API for invalid user"""
        """So response won't have a key called token in response"""
        self.assertNotIn('token', apiresponse.data)
        """Response has to return 400 Bad requests"""
        self.assertEqual(apiresponse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        apiresponse = self.client.post(TOKEN_URL, {
            'email': 'one',
            'password': ''
        })

        self.assertNotIn('token', apiresponse.data)
        self.assertEqual(apiresponse.status_code, status.HTTP_400_BAD_REQUEST)
