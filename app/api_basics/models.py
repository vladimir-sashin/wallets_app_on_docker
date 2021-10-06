from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import F

from .errors_exceptions import InsufficientFunds


class Wallet(models.Model):
    """A model of wallet that implements 'make_deposit' and 'make_transaction" actions logic in corresponding methods"""

    name = models.CharField(max_length=100, unique=True)
    holder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users_wallet"
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(
                fields=["holder"],
            ),
            models.Index(
                fields=["balance"],
            ),
        ]

    def __str__(self):
        return self.name

    def make_deposit(self, amount):
        """Implements 'make_deposit' action on wallet resource. Arguments should be validated before calling.
        Arguments:
            - 'amount' > 0 in US dollars"""
        balance_before = Wallet.objects.filter(id=self.id)[0].balance
        with transaction.atomic():
            Wallet.objects.filter(id=self.id).update(balance=F("balance") + amount)
            TransactionV2(
                wallet=self,
                recipient=self,
                amount=amount,
                transaction_type="CRED",
                balance_before=balance_before,
                balance_after=balance_before + amount,
            ).save()

    def make_transaction(self, amount, recipient_id):
        """Implements 'make_transaction' action on wallet resource. Arguments should be validated before calling.
        Arguments:
            - 'amount' > 0 in US dollars, should be >= sender's balance
            - 'recipient_id' - id of recipient wallet, should be != id of sender wallet"""
        sender_obj = Wallet.objects.filter(id=self.id)[0]
        recipient_obj = Wallet.objects.filter(id=recipient_id)[0]
        with transaction.atomic():
            if Wallet.objects.filter(id=self.id, balance__gte=amount).update(
                balance=F("balance") - amount
            ):
                # increment recipient balance
                Wallet.objects.filter(id=recipient_id).update(
                    balance=F("balance") + amount
                )
                # transaction record for debit
                TransactionV2(
                    wallet=self,
                    sender=self,
                    recipient=recipient_obj,
                    amount=amount,
                    transaction_type="DEB",
                    balance_before=sender_obj.balance + amount,
                    balance_after=sender_obj.balance,
                ).save()
                # transaction record for credit
                TransactionV2(
                    wallet=recipient_obj,
                    sender=self,
                    recipient=recipient_obj,
                    amount=amount,
                    transaction_type="CRED",
                    balance_before=recipient_obj.balance - amount,
                    balance_after=recipient_obj.balance,
                ).save()
            else:
                raise InsufficientFunds


class TransactionV2(models.Model):
    """A model of one-way transaction."""

    CREDIT = "CRED"
    DEBIT = "DEB"
    TRANSACTION_TYPES_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="current_wallet"
    )
    sender = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="sender_wallet",
        null=True,
        blank=True,
    )
    recipient = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="recipient_wallet"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transaction_type = models.CharField(
        max_length=6, choices=TRANSACTION_TYPES_CHOICES, default=CREDIT
    )
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["wallet", "timestamp"]),
            models.Index(fields=["wallet", "transaction_type", "timestamp"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["transaction_type", "timestamp"]),
        ]
