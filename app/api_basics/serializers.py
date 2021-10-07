from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .documentation_stuff import CREATE_WALLET_REQUEST_EXAMPLE
from .errors_exceptions import (
    DATERANGE_BEFORE_AFTER_ERROR,
    INSUFFICIENT_FUNDS_ERROR,
    RECIPIENT_DOESNT_EXIST_ERROR,
    RECIPIENT_IS_SENDER_ERROR,
    TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR,
)
from .models import TransactionV2, Wallet


@extend_schema_serializer(examples=[CREATE_WALLET_REQUEST_EXAMPLE])
class WalletSerializer(serializers.ModelSerializer):
    """Serializer for 'Wallet' model."""

    class Meta:
        model = Wallet
        fields = ["name", "balance"]


class DepositSerializer(serializers.Serializer):
    """Serializer for 'make_deposit' action on wallet resource."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR)
        return value


class TransactionV2Serializer(serializers.ModelSerializer):
    """Serializer for 'history' action on wallet resource to replace wallet ids with wallet names in response."""

    class Meta:
        model = TransactionV2
        fields = "__all__"

    wallet = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()

    def get_wallet(self, obj):
        return Wallet.objects.filter(id=obj.wallet.id)[0].name

    def get_sender(self, obj):
        if obj.sender:
            return Wallet.objects.filter(id=obj.sender.id)[0].name
        return obj.sender

    def get_recipient(self, obj):
        return Wallet.objects.filter(id=obj.recipient.id)[0].name


class GetHistoryParamsSerializer(serializers.Serializer):
    """Serializer for 'history' action on wallet resource to validate request parameters."""

    transaction_type_choices = TransactionV2.TRANSACTION_TYPES_CHOICES
    transaction_type = serializers.ChoiceField(
        choices=transaction_type_choices, required=False
    )
    timestamp_after = serializers.DateField(required=False)
    timestamp_before = serializers.DateField(required=False)
    ordering = serializers.ChoiceField(
        choices=[("-timestamp", "-timestamp"), ("timestamp", "timestamp")],
        required=False,
    )

    def validate(self, data):
        if (
            data.get("timestamp_before")
            and data.get("timestamp_after")
            and data.get("timestamp_before") < data.get("timestamp_after")
        ):
            raise serializers.ValidationError(DATERANGE_BEFORE_AFTER_ERROR)
        return data


class MakeTransferSerializer(serializers.Serializer):
    """Serializer for 'make_transfer' action on wallet resource to validate user input."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    recipient = serializers.CharField(max_length=100, required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR)
        try:
            balance = Wallet.objects.filter(name=self.context.get("sender"))[0].balance
        except IndexError:
            raise NotFound
        else:
            if balance < value:
                raise serializers.ValidationError(INSUFFICIENT_FUNDS_ERROR)
        return value

    def validate_recipient(self, value):
        if not Wallet.objects.filter(name=value):
            raise serializers.ValidationError(RECIPIENT_DOESNT_EXIST_ERROR)
        if self.context.get("sender") == value:
            raise serializers.ValidationError(RECIPIENT_IS_SENDER_ERROR)
        return value
