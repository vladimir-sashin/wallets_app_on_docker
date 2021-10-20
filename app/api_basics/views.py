from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r

from .documentation_stuff import (
    GET_HISTORY_CSV_RESPONSE,
    GET_HISTORY_JSON_RESPONSE,
    INSUFFICIENT_FUNDS_RESPONSE,
    MAKE_DEPOSIT_REQUEST,
    MAKE_TRANSFER_REQUEST,
    RECIPIENT_DOESNT_EXIST_RESPONSE,
    RECIPIENT_IS_SENDER_RESPONSE,
    TRANSACTION_NEGATIVE_ZERO_AMOUNT_RESPONSE,
    TRANSACTION_RESPONSE,
)
from .filters import HistoryFilter
from .models import TransactionReport, TransactionV2, Wallet
from .serializers import (
    DepositSerializer,
    GetHistoryParamsSerializer,
    MakeTransferSerializer,
    ReportsSerializer,
    TransactionV2Serializer,
    WalletSerializer,
)
from .utils import TransactionsPagination, UserWalletPermission, WalletsPagination


class ReportsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAdminUser]
    queryset = TransactionReport.objects.all()
    pagination_class = WalletsPagination
    serializer_class = ReportsSerializer


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

    @extend_schema(
        request=DepositSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[
            MAKE_DEPOSIT_REQUEST,
            TRANSACTION_RESPONSE,
            TRANSACTION_NEGATIVE_ZERO_AMOUNT_RESPONSE,
        ],
    )
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
                    "new_balance": str(Wallet.objects.filter(name=name)[0].balance),
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=MakeTransferSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        examples=[
            MAKE_TRANSFER_REQUEST,
            TRANSACTION_RESPONSE,
            TRANSACTION_NEGATIVE_ZERO_AMOUNT_RESPONSE,
            INSUFFICIENT_FUNDS_RESPONSE,
            RECIPIENT_IS_SENDER_RESPONSE,
            RECIPIENT_DOESNT_EXIST_RESPONSE,
        ],
    )
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
            wallet.make_transaction(amount=amount, recipient_id=recipient_id)
            return Response(
                {
                    "transaction_status": "success",
                    "new_balance": str(Wallet.objects.filter(name=name)[0].balance),
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[GetHistoryParamsSerializer],
        request=GetHistoryParamsSerializer,
        responses={200: OpenApiTypes.OBJECT},
        examples=[GET_HISTORY_CSV_RESPONSE, GET_HISTORY_JSON_RESPONSE],
    )
    @action(detail=True, methods=["get"], permission_classes=[UserWalletPermission])
    def history(self, request, name=None):
        """Implements 'history' action on 'wallet' resource to return all paginated transactions that satisfy applied
        filter.
            - If 'HTTP_ACCEPT' header is 'application/json', returns JSON response
            - If 'HTTP_ACCEPT' header is '*/*' or 'text/csv', returns CSV response

        Had to re-implement ordering for this action here and in GetHistoryParamsSerializer because this action
        requires Wallets model queryset from GenericViewSet.get_queryset(), and filters.OrderingFilter also uses
        this queryset, that's why it isn't possible to set ordering_fields from TransactionV2 model"""

        self.pagination_class = TransactionsPagination
        serializer = GetHistoryParamsSerializer(data=request.query_params)
        self.renderer_classes = [JSONRenderer]
        if serializer.is_valid():
            wallet_id = self.get_object().id
            initial_queryset = TransactionV2.objects.filter(wallet=wallet_id)
            transactions = HistoryFilter(
                data=serializer.validated_data, queryset=initial_queryset
            ).qs.order_by(serializer.validated_data.get("ordering", "-timestamp"))
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
