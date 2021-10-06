from django.contrib.auth.models import User
from factory import Faker, django


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("user_name")
    password = Faker("password")
