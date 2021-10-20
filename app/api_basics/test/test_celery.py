import datetime
from decimal import Decimal
from unittest.mock import patch

from api_basics.models import TransactionReport
from api_basics.tasks import generate_report
from api_basics.test.factory import HistoryFactory, WalletFactory
from django.utils import timezone
from rest_framework.test import APITestCase


class GenerateReportTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wallet_1 = WalletFactory.create(balance=0.0)
        cls.wallet_2 = WalletFactory.create(balance=0.0)
        cls.wallet_3 = WalletFactory.create(balance=0.0)
        cls.records_yesterday = [
            {
                "wallet": cls.wallet_3,
                "sender": None,
                "recipient": cls.wallet_3,
                "amount": Decimal(str(300)),
                "transaction_type": "CRED",
                "balance_before": Decimal(str(0)),
                "balance_after": Decimal(str(300)),
            },
            {
                "wallet": cls.wallet_2,
                "sender": None,
                "recipient": cls.wallet_2,
                "amount": Decimal(str(100)),
                "transaction_type": "DEB",
                "balance_before": Decimal(str(0)),
                "balance_after": Decimal(str(100)),
            },
        ]
        cls.records = [
            {
                "wallet": cls.wallet_1,
                "sender": None,
                "recipient": cls.wallet_1,
                "amount": Decimal(str(1000)),
                "transaction_type": "CRED",
                "balance_before": Decimal(str(0)),
                "balance_after": Decimal(str(1000)),
            },
            {
                "wallet": cls.wallet_1,
                "sender": cls.wallet_1,
                "recipient": cls.wallet_2,
                "amount": Decimal(str(400.55)),
                "transaction_type": "DEB",
                "balance_before": Decimal(str(1000)),
                "balance_after": Decimal(str(599.45)),
            },
            {
                "wallet": cls.wallet_2,
                "sender": cls.wallet_1,
                "recipient": cls.wallet_2,
                "amount": Decimal(str(400.55)),
                "transaction_type": "CRED",
                "balance_before": Decimal(str(100)),
                "balance_after": Decimal(str(500.55)),
            },
            {
                "wallet": cls.wallet_2,
                "sender": cls.wallet_2,
                "recipient": cls.wallet_1,
                "amount": Decimal(str(100)),
                "transaction_type": "DEB",
                "balance_before": Decimal(str(500.55)),
                "balance_after": Decimal(str(400.55)),
            },
            {
                "wallet": cls.wallet_1,
                "sender": cls.wallet_2,
                "recipient": cls.wallet_1,
                "amount": Decimal(str(100)),
                "transaction_type": "CRED",
                "balance_before": Decimal(str(599.45)),
                "balance_after": Decimal(str(699.45)),
            },
        ]

        # generate transactions in history that was 'yesterday' - they shouldn't be included in report
        with patch.object(
            timezone,
            "now",
            return_value=timezone.make_aware(datetime.datetime(2021, 10, 18, 12)),
        ):
            for kwargs in cls.records_yesterday:
                HistoryFactory.create(**kwargs)
        # generate transactions for 'today' - they should be used in report
        with patch.object(
            timezone,
            "now",
            return_value=timezone.make_aware(datetime.datetime(2021, 10, 19, 12)),
        ):
            for kwargs in cls.records:
                HistoryFactory.create(**kwargs)

    def test_generated_report(self):
        with patch.object(
            timezone,
            "now",
            return_value=timezone.make_aware(datetime.datetime(2021, 10, 19, 13)),
        ):
            generate_report.apply()

        self.assertEqual(TransactionReport.objects.all().count(), 2)
        self.assertEqual(
            TransactionReport.objects.get(wallet=self.wallet_1).debit_sum,
            Decimal(str(400.55)),
        )
        self.assertEqual(
            TransactionReport.objects.get(wallet=self.wallet_1).credit_sum,
            Decimal(str(1100)),
        )
        self.assertEqual(
            TransactionReport.objects.get(wallet=self.wallet_2).debit_sum,
            Decimal(str(100)),
        )
        self.assertEqual(
            TransactionReport.objects.get(wallet=self.wallet_2).credit_sum,
            Decimal(str(400.55)),
        )
