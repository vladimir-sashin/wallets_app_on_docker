from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.test.factory import UserFactory


class UserRegistrationTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_object = UserFactory.build()
        cls.users_saved = UserFactory.create_batch(3)
        cls.client = APIClient()
        cls.registration_url = "/api/register/"
        cls.faker_obj = Faker()

    def test_if_data_is_valid_then_register(self):
        # prepare data
        registration_dict = {
            "username": self.user_object.username,
            "password": self.user_object.password,
        }
        # make request
        response = self.client.post(self.registration_url, registration_dict)
        # assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"username": self.user_object.username})
        self.assertEqual(User.objects.count(), 4)
        # check database
        self.assertEqual(
            User.objects.get(username=self.user_object.username).username,
            self.user_object.username,
        )

    def test_if_data_is_invalid_then_error(self):
        response = self.client.post(self.registration_url, None)
        # assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "This field is required.")
        self.assertEqual(response.data["password"][0], "This field is required.")
        # assert database
        self.assertEqual(User.objects.count(), 3)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username=self.user_object.username)

    def test_if_username_is_not_unique(self):
        registration_dict = {
            "username": self.users_saved[0].username,
            "password": "password12345",
        }
        response = self.client.post(self.registration_url, registration_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"username": ["A user with that username already exists."]}
        )
        # assert database
        self.assertEqual(User.objects.count(), 3)
