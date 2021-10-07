from decimal import Decimal

from api_basics.models import Wallet
from api_basics.test.factory import WalletFactory
from api_basics.views import WalletViewSet
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.test.factory import UserFactory


class CreateWalletTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_saved = UserFactory.create()
        cls.wallets_saved = WalletFactory.create_batch(2, balance=10)
        cls.client = APIClient()
        cls.wallets_url = reverse("wallets-list")
        cls.faker_obj = Faker()

    def test_if_data_is_valid_create_wallet(self):
        request_body = {"name": "new_wallet"}
        refresh = RefreshToken.for_user(self.user_saved)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )
        response = self.client.post(self.wallets_url, request_body)
        request_body["balance"] = "0.00"
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, request_body)

        self.assertEqual(
            Wallet.objects.get(name=request_body["name"]).name, request_body["name"]
        )
        self.assertEqual(Wallet.objects.get(name=request_body["name"]).balance, 0)
        for wallet in self.wallets_saved:
            self.assertEqual(Wallet.objects.get(name=wallet.name).balance, 10)


class MakeTransferTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sender_wallet = WalletFactory.create(balance=10.79)
        cls.recipient_wallet = WalletFactory.create(balance=56.12)
        cls.client = APIClient()
        cls.transfer_url = "/api/wallets/" + cls.sender_wallet.name + "/make_transfer/"
        cls.view = WalletViewSet()
        cls.faker_obj = Faker()

    def test_transfer_happy_path(self):
        request_body = {"amount": 8.43, "recipient": self.recipient_wallet.name}
        refresh = RefreshToken.for_user(self.sender_wallet.holder)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token)
        )
        response = self.client.post(self.transfer_url, request_body)

        new_sender_balance = Decimal(str(self.sender_wallet.balance)) - Decimal(
            str(request_body.get("amount"))
        )
        new_recipient_balance = Decimal(str(self.recipient_wallet.balance)) + Decimal(
            str(request_body.get("amount"))
        )
        response_body = {
            "transaction_status": "success",
            "new_balance": str(new_sender_balance),
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, response_body)
        self.assertEqual(
            Wallet.objects.get(name=self.sender_wallet.name).balance, new_sender_balance
        )
        self.assertEqual(
            Wallet.objects.get(name=self.recipient_wallet.name).balance,
            new_recipient_balance,
        )
