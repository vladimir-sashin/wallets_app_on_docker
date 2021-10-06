from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r

from .errors_exceptions import InsufficientFunds
from .filters import HistoryFilter
from .models import TransactionV2, Wallet
from .serializers import (
    DepositSerializer,
    GetHistoryParamsSerializer,
    MakeTransferSerializer,
    TransactionV2Serializer,
    WalletSerializer,
)
from .utils import TransactionsPagination, UserWalletPermission, WalletsPagination


class WalletViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """View for 'wallets' resource"""

    permission_classes = [IsAuthenticated, UserWalletPermission]
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = "name"
    pagination_class = WalletsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "id", "balance"]
    ordering = ["-id"]
    renderer_classes = (r.CSVRenderer,) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)

    def get_queryset(self):
        """'list' action will return only those wallets that are owned by user."""
        if self.action == "list":
            user = self.request.user
            return Wallet.objects.filter(holder=user)
        elif (
            self.action == "retrieve"
            or self.action == "make_deposit"
            or self.action == "make_transfer"
            or self.action == "history"
        ):
            return super().get_queryset()

    def get_renderers(self):
        """Method to exclude 'CSVRenderer' from this view 'renderer_classes' for all actions except history.
        - 'history' action returns response in csv by default
        - all other actions return JSON response by default"""
        if self.action != "history":
            return [
                renderer()
                for renderer in self.renderer_classes
                if renderer != r.CSVRenderer
            ]
        else:
            return super().get_renderers()

    def perform_create(self, serializer):
        """To set current user as wallet's holder on it's creation"""
        serializer.save(holder=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[UserWalletPermission])
    def make_deposit(self, request, name=None):
        """Implements 'make_deposit' action on 'wallet' resource.
        Calls Wallet.make_deposit method using serializer's validated data."""
        serializer = DepositSerializer(data=request.data)
        wallet = self.get_object()
        if serializer.is_valid():
            wallet.make_deposit(serializer.validated_data.get("amount"))
            return Response(
                {
                    "transaction_status": "success",
                    "new_balance": Wallet.objects.filter(name=name)[0].balance,
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[UserWalletPermission])
    def make_transfer(self, request, name=None):
        """Implements 'make_transfer' action on 'wallet' resource.
        Makes additional validations and calls Wallet.make_transfer method using serializer's validated data."""
        serializer = MakeTransferSerializer(data=request.data, context={"sender": name})
        if serializer.is_valid():
            wallet = self.get_object()
            amount = serializer.validated_data.get("amount")
            recipient_name = serializer.validated_data.get("recipient")
            recipient_id = Wallet.objects.filter(name=recipient_name)[0].id
            if wallet.balance < amount:
                raise InsufficientFunds
            wallet.make_transaction(amount=amount, recipient_id=recipient_id)
            return Response(
                {
                    "transaction_status": "success",
                    "new_balance": Wallet.objects.filter(name=name)[0].balance,
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[UserWalletPermission])
    def history(self, request, name=None):
        """Implements 'history' action on 'wallet' resource to return all paginated transactions that satisfy applied
        filter.
            - If 'HTTP_ACCEPT' header is 'application/json', returns JSON response
            - If 'HTTP_ACCEPT' header is '*/*' or 'text/csv', returns CSV response"""
        self.pagination_class = TransactionsPagination
        serializer = GetHistoryParamsSerializer(data=request.query_params)
        self.renderer_classes = [JSONRenderer]
        if serializer.is_valid():
            wallet_id = self.get_object().id
            initial_queryset = TransactionV2.objects.filter(wallet=wallet_id)
            transactions = HistoryFilter(
                data=request.query_params, queryset=initial_queryset
            ).qs.order_by("-timestamp")
            if request.META.get("HTTP_ACCEPT") == "application/json":
                return self.get_paginated_response(
                    TransactionV2Serializer(
                        self.paginate_queryset(transactions), many=True
                    ).data
                )
            else:
                return Response(
                    TransactionV2Serializer(
                        self.paginate_queryset(transactions), many=True
                    ).data
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
